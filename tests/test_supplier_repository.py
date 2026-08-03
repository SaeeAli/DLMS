from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from database.base import Base
from models.supplier import Supplier
from repositories.supplier_repository import SupplierRepository


def test_supplier_repository_persists_supplier_fields() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        repository = SupplierRepository(session)
        created = repository.create(
            Supplier(
                name="MedTech GmbH",
                country="Germany",
                city="Berlin",
                address="Street 1",
                contact_person="Anna",
                email="anna@medtech.com",
                phone="+49-123",
                on_site_calibration=True,
                exchange_device_available=True,
                shipping_supported=False,
                currency="EUR (€)",
                default_calibration_lead_time_days=7,
            )
        )

        assert created.id is not None
        fetched = repository.get_by_id(created.id)
        assert fetched is not None
        assert fetched.name == "MedTech GmbH"
        assert fetched.country == "Germany"
        assert fetched.contact_person == "Anna"
        assert fetched.currency == "EUR (€)"
        assert fetched.default_calibration_lead_time_days == 7
