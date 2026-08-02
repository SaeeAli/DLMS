import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication
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
from services.site_service import SiteService
from ui.pages.site_list_page import SiteListPage


def test_site_list_page_loads_and_filters_sites() -> None:
    app = QApplication.instance() or QApplication([])
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        customer_repository = CustomerRepository(session)
        study_repository = StudyRepository(session)
        country_repository = CountryRepository(session)
        study_country_repository = StudyCountryRepository(session)
        site_repository = SiteRepository(session)

        country_service = CountryService(study_country_repository, country_repository, study_repository, site_repository)
        site_service = SiteService(site_repository, study_country_repository)

        customer = Customer(name="Acme")
        customer_repository.create(customer)
        study = Study(study_number="ST-100", customer=customer)
        study_repository.create(study)

        assignment = country_service.create_country(study=study, name="Germany", country_code="DE")
        site_service.create_site(study_country=assignment, site_number="S-100", name="Berlin Site")

        page = SiteListPage(site_service)
        page.refresh_sites()

        assert page.table_model.rowCount() == 1
        page.search_input.setText("berlin")
        assert page.table_model.rowCount() == 1
        page.search_input.setText("missing")
        assert page.table_model.rowCount() == 0

    app.quit()
