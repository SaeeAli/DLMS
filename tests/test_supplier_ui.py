import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from database.base import Base
from repositories.supplier_repository import SupplierRepository
from services.supplier_service import SupplierService
from ui.pages.supplier_list_page import SupplierListPage
from ui.widgets.supplier_form_dialog import SupplierFormDialog


def test_supplier_list_page_loads_and_filters_suppliers() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        service = SupplierService(SupplierRepository(session))
        page = SupplierListPage(service)

        service.create_supplier(
            name="MedTech GmbH",
            country="Germany",
            contact_person="Anna",
            currency="EUR (€)",
            default_calibration_lead_time_days=5,
        )
        page.refresh_suppliers()

        assert page.table_model.rowCount() == 1
        assert page.table_model.headerData(0, Qt.Orientation.Horizontal) == "Supplier Name"
        assert page.table_model.headerData(1, Qt.Orientation.Horizontal) == "Country"
        assert page.table_model.headerData(4, Qt.Orientation.Horizontal) == "Contact Person"

        page.search_input.setText("medtech")
        assert page.table_model.rowCount() == 1
        page.search_input.setText("germany")
        assert page.table_model.rowCount() == 1
        page.search_input.setText("anna")
        assert page.table_model.rowCount() == 1
        page.search_input.setText("missing")
        assert page.table_model.rowCount() == 0


def test_supplier_form_dialog_currency_is_non_editable_and_limited_values() -> None:
    dialog = SupplierFormDialog(["EUR (€)", "USD ($)"])

    assert dialog.currency_combo.isEditable() is False
    options = [dialog.currency_combo.itemText(i) for i in range(dialog.currency_combo.count())]
    assert options == ["EUR (€)", "USD ($)"]
