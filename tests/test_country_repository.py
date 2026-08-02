from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from database.base import Base
from models.country import Country
from models.customer import Customer
from models.study import Study
from models.study_country import StudyCountry
from repositories.country_repository import CountryRepository
from repositories.customer_repository import CustomerRepository
from repositories.study_country_repository import StudyCountryRepository
from repositories.study_repository import StudyRepository


def test_country_repository_persists_and_allows_same_name_across_studies() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        customer_repository = CustomerRepository(session)
        study_repository = StudyRepository(session)
        country_repository = CountryRepository(session)
        study_country_repository = StudyCountryRepository(session)

        customer = Customer(name="Acme")
        customer_repository.create(customer)

        study_one = Study(study_number="ST-100", customer=customer)
        study_two = Study(study_number="ST-101", customer=customer)
        study_repository.create(study_one)
        study_repository.create(study_two)

        country = Country(name="Germany", country_code="DE")
        country_repository.create(country)
        assignment_one = StudyCountry(study=study_one, country=country, status="Active")
        assignment_two = StudyCountry(study=study_two, country=country, status="Active")
        study_country_repository.create(assignment_one)
        study_country_repository.create(assignment_two)

        saved = study_country_repository.get_all()
        assert len(saved) == 2
        assert {assignment.study_id for assignment in saved} == {study_one.id, study_two.id}
