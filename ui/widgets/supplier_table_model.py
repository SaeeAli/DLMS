from __future__ import annotations

from typing import Any

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from models.supplier import Supplier


class SupplierTableModel(QAbstractTableModel):
    """Table model for displaying suppliers in a QTableView."""

    def __init__(self, suppliers: list[Supplier] | None = None) -> None:
        super().__init__()
        self._suppliers = suppliers or []
        self._filter = ""

    def rowCount(self, parent: QModelIndex | None = None) -> int:
        return len(self._filtered_suppliers())

    def columnCount(self, parent: QModelIndex | None = None) -> int:
        return 12

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return None

        supplier = self._filtered_suppliers()[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 0:
                return supplier.name
            if index.column() == 1:
                return supplier.country or ""
            if index.column() == 2:
                return supplier.city or ""
            if index.column() == 3:
                return supplier.address or ""
            if index.column() == 4:
                return supplier.contact_person or ""
            if index.column() == 5:
                return supplier.email or ""
            if index.column() == 6:
                return supplier.phone or ""
            if index.column() == 7:
                return "Yes" if supplier.on_site_calibration else "No"
            if index.column() == 8:
                return "Yes" if supplier.exchange_device_available else "No"
            if index.column() == 9:
                return "Yes" if supplier.shipping_supported else "No"
            if index.column() == 10:
                return supplier.currency
            if index.column() == 11:
                return supplier.default_calibration_lead_time_days
        return None

    def headerData(self, section: int, orientation: int, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            headers = [
                "Supplier Name",
                "Country",
                "City",
                "Address",
                "Contact Person",
                "Email",
                "Phone",
                "On-site Calibration",
                "Exchange Device Available",
                "Shipping Supported",
                "Currency",
                "Default Calibration Lead Time (Days)",
            ]
            return headers[section]
        return None

    def set_suppliers(self, suppliers: list[Supplier]) -> None:
        self.beginResetModel()
        self._suppliers = suppliers
        self.endResetModel()

    def set_filter(self, query: str) -> None:
        self.beginResetModel()
        self._filter = query.lower()
        self.endResetModel()

    def supplier_id_at(self, row: int) -> str | None:
        suppliers = self._filtered_suppliers()
        if 0 <= row < len(suppliers):
            return suppliers[row].id
        return None

    def _filtered_suppliers(self) -> list[Supplier]:
        if not self._filter:
            return self._suppliers

        query = self._filter
        return [
            supplier
            for supplier in self._suppliers
            if query in (supplier.name or "").lower()
            or query in (supplier.country or "").lower()
            or query in (supplier.contact_person or "").lower()
        ]
