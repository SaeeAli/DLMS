import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from database.base import Base
from repositories.customer_repository import CustomerRepository
from services.customer_service import CustomerService


def test_customer_service_crud_and_validation() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        service = CustomerService(CustomerRepository(session))

        created = service.create_customer(name="Acme")
        assert created.id is not None

        fetched = service.get_by_id(created.id)
        assert fetched is not None
        assert fetched.name == "Acme"

        updated = service.update_customer(
            fetched,
            name="Acme Corp",
            contact_email="sales@example.com",
        )
        assert updated.name == "Acme Corp"

        with pytest.raises(ValueError, match="name is required"):
            service.create_customer(name="   ")

        results = service.search_customers("acme")
        assert len(results) == 1

        service.delete_customer(updated)
        assert service.get_by_id(created.id) is None
