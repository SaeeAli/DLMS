import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from database.base import Base
from models.customer import Customer
from models.study import Study
from repositories.customer_repository import CustomerRepository
from repositories.study_repository import StudyRepository
from services.study_service import StudyService


def test_study_service_prevents_duplicate_study_number_per_customer() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        customer_repository = CustomerRepository(session)
        study_repository = StudyRepository(session)
        service = StudyService(study_repository, customer_repository)

        customer = Customer(name="Acme", customer_code="ACM-001")
        customer_repository.create(customer)

        service.create_study(customer=customer, study_number="ST-100", study_name="Pilot", status="Active")

        with pytest.raises(ValueError, match="already exists"):
            service.create_study(customer=customer, study_number="ST-100", study_name="Second", status="Active")


def test_study_service_allows_same_study_number_for_different_customers() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        customer_repository = CustomerRepository(session)
        study_repository = StudyRepository(session)
        service = StudyService(study_repository, customer_repository)

        customer_one = Customer(name="Acme", customer_code="ACM-001")
        customer_two = Customer(name="Beta", customer_code="BET-001")
        customer_repository.create(customer_one)
        customer_repository.create(customer_two)

        first = service.create_study(customer=customer_one, study_number="ST-100", study_name="Pilot", status="Active")
        second = service.create_study(customer=customer_two, study_number="ST-100", study_name="Follow-up", status="Completed")

        assert first.customer_id == customer_one.id
        assert second.customer_id == customer_two.id
