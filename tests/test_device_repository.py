from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from database.base import Base
from models.device import Device
from repositories.device_repository import DeviceRepository


def test_device_repository_persists_required_fields_and_legacy_asset_number() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        repository = DeviceRepository(session)
        created = repository.create(
            Device(
                brand="Fluke",
                device_type="Thermometer",
                model="T300",
                serial_number="SN-101",
                asset_number="Fluke",
            )
        )

        assert created.id is not None
        fetched = repository.get_by_id(created.id)
        assert fetched is not None
        assert fetched.brand == "Fluke"
        assert fetched.device_type == "Thermometer"
        assert fetched.model == "T300"
        assert fetched.serial_number == "SN-101"
        assert fetched.asset_number == "Fluke"
