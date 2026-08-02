import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from database.base import Base
from repositories.device_repository import DeviceRepository
from services.device_service import DeviceService
from ui.pages.device_list_page import DeviceListPage
from ui.widgets.device_form_dialog import DeviceFormDialog


def test_device_list_page_loads_and_filters_devices() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        service = DeviceService(DeviceRepository(session))
        page = DeviceListPage(service)

        service.create_device(brand="Fluke", device_type="Thermometer", serial_number="SN-100", model="Model X")
        page.refresh_devices()

        assert page.table_model.rowCount() == 1
        assert page.table_model.headerData(0, Qt.Orientation.Horizontal) == "Brand"
        assert page.table_model.headerData(1, Qt.Orientation.Horizontal) == "Type of Device"
        assert page.table_model.headerData(2, Qt.Orientation.Horizontal) == "Model"
        assert page.table_model.headerData(3, Qt.Orientation.Horizontal) == "Serial Number"
        page.search_input.setText("SN-100")
        assert page.table_model.rowCount() == 1
        page.search_input.setText("missing")
        assert page.table_model.rowCount() == 0


def test_device_form_dialog_uses_required_type_options() -> None:
    dialog = DeviceFormDialog()
    options = [dialog.device_type_combo.itemText(i) for i in range(dialog.device_type_combo.count())]

    assert options == [
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
