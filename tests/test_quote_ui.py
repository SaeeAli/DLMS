import os
from datetime import datetime, timezone

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from database.base import Base
from models.country import Country
from models.customer import Customer
from models.quote import Quote
from models.quote_site import QuoteSite
from models.site import Site
from models.study import Study
from models.study_country import StudyCountry
from repositories.country_repository import CountryRepository
from repositories.customer_repository import CustomerRepository
from repositories.quote_repository import QuoteRepository
from repositories.site_repository import SiteRepository
from repositories.study_country_repository import StudyCountryRepository
from repositories.study_repository import StudyRepository
from services.quote_service import QuoteService
from ui.pages.quote_list_page import QuoteListPage
from ui.widgets.quote_form_dialog import QuoteFormDialog


def _make_service(session: Session) -> QuoteService:
    return QuoteService(
        QuoteRepository(session),
        CustomerRepository(session),
        StudyRepository(session),
        StudyCountryRepository(session),
        SiteRepository(session),
        CountryRepository(session),
    )


def test_quote_list_page_loads_and_filters_quotes() -> None:
    app = QApplication.instance() or QApplication([])
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        service = _make_service(session)

        customer = Customer(name="Acme")
        study = Study(study_number="ST-100", customer=customer)
        country = Country(name="Germany")
        assignment = StudyCountry(study=study, country=country)
        site = Site(name="Berlin Site", site_number="S-001", study_country=assignment)
        site_two = Site(name="Munich Site", site_number="S-002", study_country=assignment)
        quote = Quote(
            quote_number="Q-001",
            quote_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
            status="Draft",
        )
        quote.quote_sites = [QuoteSite(site=site), QuoteSite(site=site_two)]
        session.add_all([customer, study, country, assignment, site, site_two, quote])
        session.flush()

        page = QuoteListPage(service)
        page.refresh_quotes()

        assert page.table_model.rowCount() == 1
        page.search_input.setText("q-001")
        assert page.table_model.rowCount() == 1
        page.search_input.setText("s-002")
        assert page.table_model.rowCount() == 1
        page.search_input.setText("missing")
        assert page.table_model.rowCount() == 0

    app.quit()


def test_quote_form_dialog_filters_in_customer_study_country_site_order() -> None:
    app = QApplication.instance() or QApplication([])
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        customer_one = Customer(name="Acme")
        customer_two = Customer(name="Beta")
        study_one = Study(study_number="ST-100", customer=customer_one)
        study_two = Study(study_number="ST-200", customer=customer_two)
        country_one = Country(name="Germany")
        country_two = Country(name="France")
        assignment_one = StudyCountry(study=study_one, country=country_one)
        assignment_two = StudyCountry(study=study_two, country=country_two)
        site_one = Site(name="Berlin Site", site_number="S-001", study_country=assignment_one)
        site_two = Site(name="Paris Site", site_number="S-002", study_country=assignment_two)
        session.add_all([
            customer_one,
            customer_two,
            study_one,
            study_two,
            country_one,
            country_two,
            assignment_one,
            assignment_two,
            site_one,
            site_two,
        ])
        session.flush()

        dialog = QuoteFormDialog(
            [customer_one, customer_two],
            [study_one, study_two],
            [country_one, country_two],
            [site_one, site_two],
        )

        customer_index = dialog.customer_combo.findData(customer_one.id)
        dialog.customer_combo.setCurrentIndex(customer_index)

        study_texts = [dialog.study_combo.itemText(i) for i in range(dialog.study_combo.count())]
        assert "ST-100" in study_texts
        assert "ST-200" not in study_texts

        study_index = dialog.study_combo.findData(study_one.id)
        dialog.study_combo.setCurrentIndex(study_index)

        country_texts = [dialog.country_combo.itemText(i) for i in range(dialog.country_combo.count())]
        assert "Germany" in country_texts
        assert "France" not in country_texts

        country_index = dialog.country_combo.findData(country_one.id)
        dialog.country_combo.setCurrentIndex(country_index)

        site_texts = [dialog.site_list.item(i).text() for i in range(dialog.site_list.count())]
        assert "S-001" in site_texts
        assert "S-002" not in site_texts

        selected_ids = dialog.selected_site_ids()
        assert selected_ids == []

    app.quit()


def test_quote_form_dialog_set_quote_preselects_multiple_sites() -> None:
    app = QApplication.instance() or QApplication([])
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        customer = Customer(name="Acme")
        study = Study(study_number="ST-100", customer=customer)
        country = Country(name="Germany")
        assignment = StudyCountry(study=study, country=country)
        site_one = Site(name="Berlin Site", site_number="S-001", study_country=assignment)
        site_two = Site(name="Munich Site", site_number="S-002", study_country=assignment)
        quote = Quote(
            quote_number="Q-010",
            quote_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
            status="Draft",
        )
        quote.quote_sites = [QuoteSite(site=site_one), QuoteSite(site=site_two)]
        session.add_all([customer, study, country, assignment, site_one, site_two, quote])
        session.flush()

        dialog = QuoteFormDialog([customer], [study], [country], [site_one, site_two])
        dialog.set_quote(quote)

        selected_ids = set(dialog.selected_site_ids())
        assert selected_ids == {site_one.id, site_two.id}

    app.quit()
