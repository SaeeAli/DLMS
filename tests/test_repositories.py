from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from database.base import Base
from models.customer import Customer
from repositories.base_repository import BaseRepository


def test_base_repository_crud_operations() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        repository = BaseRepository[Customer](session, Customer)

        customer = Customer(name="Acme", contact_email="ops@example.com")
        created = repository.create(customer)
        assert created.id is not None
        assert repository.exists(created.id)

        fetched = repository.get_by_id(created.id)
        assert fetched is not None
        assert fetched.name == "Acme"

        fetched.name = "Acme Corp"
        updated = repository.update(fetched)
        assert updated.name == "Acme Corp"

        repository.delete(updated)
        assert repository.get_by_id(created.id) is None

        assert repository.get_all() == []
