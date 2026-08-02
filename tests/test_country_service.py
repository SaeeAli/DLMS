import pytest
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


def test_country_service_prevents_duplicates_and_requires_study() -> None:
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

        service.create_country(study=study, name="Germany", country_code="DE", status="Active")

        with pytest.raises(ValueError, match="already exists"):
            service.create_country(study=study, name="Germany", status="Active")

        with pytest.raises(ValueError, match="study is required"):
            service.create_country(study=None, name="France", status="Active")
