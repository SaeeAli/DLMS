import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from database.base import Base
from models.customer import Customer
from repositories.customer_repository import CustomerRepository
from services.customer_service import CustomerService


def test_customer_service_validates_required_fields() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        service = CustomerService(CustomerRepository(session))

        with pytest.raises(ValueError, match="name is required"):
            service.create_customer(name="   ")


def test_customer_service_creates_customer() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        service = CustomerService(CustomerRepository(session))
        customer = service.create_customer(name="Acme")

        assert isinstance(customer, Customer)
        assert customer.name == "Acme"
