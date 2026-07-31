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

        created = service.create_device(asset_tag="Thermo-001", serial_number="SN-100", model="Model A")
        assert created.id is not None

        fetched = service.get_by_id(created.id)
        assert fetched is not None
        assert fetched.asset_tag == "Thermo-001"

        updated = service.update_device(fetched, asset_tag="Thermo-002", serial_number="SN-200", model="Model B")
        assert updated.asset_tag == "Thermo-002"

        try:
            service.create_device(asset_tag="Thermo-003", serial_number="SN-200")
        except ValueError as error:
            assert "already exists" in str(error)
        else:
            raise AssertionError("duplicate serial number should have raised")

        service.delete_device(updated)
        assert service.get_by_id(created.id) is None
