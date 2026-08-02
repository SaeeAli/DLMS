from __future__ import annotations

from typing import Any

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from models.customer import Customer


class CustomerTableModel(QAbstractTableModel):
    """Table model for displaying customers in a QTableView."""

    def __init__(self, customers: list[Customer] | None = None) -> None:
        super().__init__()
        self._customers = customers or []
        self._filter = ""

    def rowCount(self, parent: QModelIndex | None = None) -> int:
        return len(self._filtered_customers())

    def columnCount(self, parent: QModelIndex | None = None) -> int:
        return 4

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return None

        customer = self._filtered_customers()[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 0:
                return customer.name
            if index.column() == 1:
                return customer.customer_code
            if index.column() == 2:
                return customer.contact_email or ""
            if index.column() == 3:
                return customer.created_at.strftime("%Y-%m-%d") if customer.created_at else ""
        return None

    def headerData(self, section: int, orientation: int, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            headers = ["Name", "Customer Code", "Contact Email", "Created"]
            return headers[section]
        return None

    def set_customers(self, customers: list[Customer]) -> None:
        self.beginResetModel()
        self._customers = customers
        self.endResetModel()

    def set_filter(self, query: str) -> None:
        self.beginResetModel()
        self._filter = query.lower()
        self.endResetModel()

    def customer_id_at(self, row: int) -> str | None:
        customers = self._filtered_customers()
        if 0 <= row < len(customers):
            return customers[row].id
        return None

    def _filtered_customers(self) -> list[Customer]:
        if not self._filter:
            return self._customers

        query = self._filter
        return [
            customer
            for customer in self._customers
            if query in customer.name.lower()
            or query in customer.customer_code.lower()
            or query in (customer.contact_email or "").lower()
        ]
