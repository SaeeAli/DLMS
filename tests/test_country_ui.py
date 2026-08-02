import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QMessageBox
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from database.base import Base
from models.customer import Customer
from models.study import Study
from repositories.country_repository import CountryRepository
from repositories.customer_repository import CustomerRepository
from repositories.site_repository import SiteRepository
from repositories.study_country_repository import StudyCountryRepository
from repositories.study_repository import StudyRepository
from services.country_service import CountryService
from ui.pages.country_list_page import CountryListPage
from ui.widgets.country_form_dialog import CountryFormDialog


def test_country_list_page_loads_and_filters_countries() -> None:
    app = QApplication.instance() or QApplication([])
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        customer_repository = CustomerRepository(session)
        study_repository = StudyRepository(session)
        country_repository = CountryRepository(session)
        site_repository = SiteRepository(session)
        study_country_repository = StudyCountryRepository(session)
        service = CountryService(study_country_repository, country_repository, study_repository, site_repository)

        customer = Customer(name="Acme")
        customer_repository.create(customer)
        study = Study(study_number="ST-100", customer=customer)
        study_repository.create(study)
        service.create_country_record(study=study, country_name="Germany", site_number="S-100", status="Active")

        page = CountryListPage(service)
        page.refresh_countries()

        assert page.table_model.rowCount() == 1
        page.search_input.setText("s-100")
        assert page.table_model.rowCount() == 1
        page.search_input.setText("missing")
        assert page.table_model.rowCount() == 0

    app.quit()


def test_country_list_page_selection_uses_site_primary_key_for_edit_and_delete(monkeypatch) -> None:
    app = QApplication.instance() or QApplication([])
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        customer_repository = CustomerRepository(session)
        study_repository = StudyRepository(session)
        country_repository = CountryRepository(session)
        site_repository = SiteRepository(session)
        study_country_repository = StudyCountryRepository(session)
        service = CountryService(study_country_repository, country_repository, study_repository, site_repository)

        customer = Customer(name="Acme")
        customer_repository.create(customer)
        study = Study(study_number="ST-100", customer=customer)
        study_repository.create(study)
        created = service.create_country_record(study=study, country_name="Germany", site_number="S-101", status="Active")

        page = CountryListPage(service)
        page.refresh_countries()
        page.table_view.selectRow(0)

        assert page._selected_country_id == created.id
        assert service.get_country_record_by_id(page._selected_country_id) is not None

        # Ensure delete path resolves selected row by Site.id and removes the row.
        monkeypatch.setattr(
            "ui.pages.country_list_page.QMessageBox.question",
            lambda *args, **kwargs: QMessageBox.StandardButton.Yes,
        )
        page.delete_selected_country()
        page.refresh_countries()
        assert page.table_model.rowCount() == 0

    app.quit()


def test_country_form_filters_studies_by_selected_customer_and_shows_study_number_only() -> None:
    app = QApplication.instance() or QApplication([])
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        customer_repository = CustomerRepository(session)
        study_repository = StudyRepository(session)

        customer_one = Customer(name="PSI")
        customer_two = Customer(name="ACME")
        customer_repository.create(customer_one)
        customer_repository.create(customer_two)

        study_one = Study(study_number="123", customer=customer_one)
        study_two = Study(study_number="456", customer=customer_two)
        study_repository.create(study_one)
        study_repository.create(study_two)

        dialog = CountryFormDialog([customer_one, customer_two], [study_one, study_two])

        index = dialog.customer_combo.findData(customer_one.id)
        dialog.customer_combo.setCurrentIndex(index)

        study_texts = [dialog.study_combo.itemText(i) for i in range(dialog.study_combo.count())]
        assert "123" in study_texts
        assert "456" not in study_texts
        assert all(" - " not in text for text in study_texts if text)

    app.quit()
