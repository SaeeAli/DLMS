import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from database.base import Base
from repositories.supplier_repository import SupplierRepository
from services.supplier_service import SupplierService


def test_supplier_service_create_update_search_delete() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        service = SupplierService(SupplierRepository(session))

        created = service.create_supplier(
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
        assert created.id is not None

        fetched = service.get_by_id(created.id)
        assert fetched is not None
        assert fetched.name == "MedTech GmbH"

        updated = service.update_supplier(
            fetched,
            name="MedTech USA",
            country="United States",
            city="Boston",
            address="Street 2",
            contact_person="John",
            email="john@medtech.com",
            phone="+1-555",
            on_site_calibration=False,
            exchange_device_available=False,
            shipping_supported=True,
            currency="USD ($)",
            default_calibration_lead_time_days=10,
        )
        assert updated.name == "MedTech USA"
        assert updated.currency == "USD ($)"

        by_name = service.search_suppliers("medtech")
        by_country = service.search_suppliers("united states")
        by_contact = service.search_suppliers("john")
        assert len(by_name) == 1
        assert len(by_country) == 1
        assert len(by_contact) == 1

        service.delete_supplier(updated)
        assert service.get_by_id(created.id) is None


def test_supplier_service_validations() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        service = SupplierService(SupplierRepository(session))

        with pytest.raises(ValueError, match="name is required"):
            service.create_supplier(name="   ", currency="EUR (€)", default_calibration_lead_time_days=1)

        service.create_supplier(name="Unique Supplier", currency="EUR (€)", default_calibration_lead_time_days=1)
        with pytest.raises(ValueError, match="already exists"):
            service.create_supplier(name="unique supplier", currency="USD ($)", default_calibration_lead_time_days=3)

        with pytest.raises(ValueError, match="email format is invalid"):
            service.create_supplier(name="Email Supplier", email="invalid-email", currency="EUR (€)", default_calibration_lead_time_days=2)

        with pytest.raises(ValueError, match="currency must be one of"):
            service.create_supplier(name="Currency Supplier", currency="GBP", default_calibration_lead_time_days=2)

        with pytest.raises(ValueError, match="positive integer"):
            service.create_supplier(name="Lead Time Supplier", currency="EUR (€)", default_calibration_lead_time_days=0)


def test_supplier_service_currency_options_are_fixed() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        service = SupplierService(SupplierRepository(session))
        assert service.get_currency_options() == ["EUR (€)", "USD ($)"]
