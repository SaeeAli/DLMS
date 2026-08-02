from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from database.base import Base
from models.country import Country
from models.customer import Customer
from models.study import Study
from repositories.country_repository import CountryRepository
from repositories.customer_repository import CustomerRepository
from repositories.site_repository import SiteRepository
from repositories.study_country_repository import StudyCountryRepository
from repositories.study_repository import StudyRepository
from services.country_service import CountryService
from services.site_service import SiteService


def test_site_service_prevents_duplicate_site_number_per_study_country() -> None:
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

        created = country_service.create_country_record(study=study, country_name="Germany", site_number="S-000", status="Active")
        assignment = created.study_country
        site_service.create_site(study_country=assignment, site_number="S-001", name="Berlin Site")

        try:
            site_service.create_site(study_country=assignment, site_number="S-001", name="Berlin Site Duplicate")
        except ValueError as error:
            assert "already exists" in str(error)
        else:
            raise AssertionError("duplicate site number should have raised")
