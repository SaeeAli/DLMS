from __future__ import annotations

from typing import Any

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from models.device import Device


class DeviceTableModel(QAbstractTableModel):
    """Table model for displaying devices in a QTableView."""

    def __init__(self, devices: list[Device] | None = None) -> None:
        super().__init__()
        self._devices = devices or []
        self._filter = ""

    def rowCount(self, parent: QModelIndex | None = None) -> int:
        return len(self._filtered_devices())

    def columnCount(self, parent: QModelIndex | None = None) -> int:
        return 4

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return None

        device = self._filtered_devices()[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 0:
                return device.brand or ""
            if index.column() == 1:
                return device.device_type or ""
            if index.column() == 2:
                return device.model or ""
            if index.column() == 3:
                return device.serial_number or ""
        return None

    def headerData(self, section: int, orientation: int, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            headers = ["Brand", "Type of Device", "Model", "Serial Number"]
            return headers[section]
        return None

    def set_devices(self, devices: list[Device]) -> None:
        self.beginResetModel()
        self._devices = devices
        self.endResetModel()

    def set_filter(self, query: str) -> None:
        self.beginResetModel()
        self._filter = query.lower()
        self.endResetModel()

    def device_id_at(self, row: int) -> str | None:
        devices = self._filtered_devices()
        if 0 <= row < len(devices):
            return devices[row].id
        return None

    def _filtered_devices(self) -> list[Device]:
        if not self._filter:
            return self._devices

        query = self._filter
        return [
            device
            for device in self._devices
            if query in (device.serial_number or "").lower()
            or query in (device.brand or device.asset_tag or "").lower()
            or query in (device.device_type or "").lower()
            or query in (device.model or "").lower()
        ]
