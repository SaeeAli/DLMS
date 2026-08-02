from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from database.base import Base
from repositories.device_repository import DeviceRepository
from services.device_service import DeviceService


def test_device_service_persists_and_prevents_duplicate_serials() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        service = DeviceService(DeviceRepository(session))

        created = service.create_device(brand="Fluke", device_type="Thermometer", serial_number="SN-100", model="Model A")
        assert created.id is not None

        fetched = service.get_by_id(created.id)
        assert fetched is not None
        assert fetched.brand == "Fluke"
        assert fetched.device_type == "Thermometer"

        updated = service.update_device(fetched, brand="Keysight", device_type="Defibrillator", serial_number="SN-200", model="Model B")
        assert updated.brand == "Keysight"
        assert updated.device_type == "Defibrillator"

        try:
            service.create_device(brand="Tektronix", device_type="Other", serial_number="SN-200")
        except ValueError as error:
            assert "already exists" in str(error)
        else:
            raise AssertionError("duplicate serial number should have raised")

        service.delete_device(updated)
        assert service.get_by_id(created.id) is None


def test_device_service_maps_legacy_device_name_to_brand() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        repository = DeviceRepository(session)
        # Simulate legacy record where Device Name lived in asset_number.
        legacy = repository.model_type(asset_number="Legacy-Device", serial_number="SN-900")
        repository.create(legacy)

        service = DeviceService(repository)
        migrated = service.get_by_id(legacy.id)

        assert migrated is not None
        assert migrated.brand == "Legacy-Device"


def test_device_service_returns_required_device_type_options() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        service = DeviceService(DeviceRepository(session))

        assert service.get_device_type_options() == [
            "Centrifuge",
            "ECG",
            "Freezer",
            "Refrigerator",
            "Incubator",
            "Infusion Pump",
            "Syringe Pump",
            "Temperature Logger",
            "Pipette",
            "Balance",
            "Blood Pressure Monitor",
            "Thermometer",
            "Defibrillator",
            "Other",
        ]
