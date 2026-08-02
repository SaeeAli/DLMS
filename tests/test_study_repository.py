from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from database.base import Base
from models.customer import Customer
from models.study import Study
from repositories.customer_repository import CustomerRepository
from repositories.study_repository import StudyRepository


def test_study_repository_persists_and_groups_by_customer() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        customer_repository = CustomerRepository(session)
        study_repository = StudyRepository(session)

        customer_one = Customer(name="Acme")
        customer_two = Customer(name="Beta")
        customer_repository.create(customer_one)
        customer_repository.create(customer_two)

        study_one = Study(study_number="ST-100", customer=customer_one, status="Active")
        study_two = Study(study_number="ST-100", customer=customer_two, status="Completed")
        study_repository.create(study_one)
        study_repository.create(study_two)

        all_studies = study_repository.get_all()
        assert len(all_studies) == 2
        assert {study.customer_id for study in all_studies} == {customer_one.id, customer_two.id}
