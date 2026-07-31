import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from database.base import Base
from repositories.device_repository import DeviceRepository
from services.device_service import DeviceService
from ui.pages.device_list_page import DeviceListPage


def test_device_list_page_loads_and_filters_devices() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        service = DeviceService(DeviceRepository(session))
        page = DeviceListPage(service)

        service.create_device(asset_tag="Thermo-001", serial_number="SN-100", model="Model X")
        page.refresh_devices()

        assert page.table_model.rowCount() == 1
        page.search_input.setText("SN-100")
        assert page.table_model.rowCount() == 1
        page.search_input.setText("missing")
        assert page.table_model.rowCount() == 0
