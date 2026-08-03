from __future__ import annotations

from typing import Any

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from models.calibration import Calibration


class CalibrationTableModel(QAbstractTableModel):
    """Table model for displaying calibrations in a QTableView."""

    def __init__(self, calibrations: list[Calibration] | None = None) -> None:
        super().__init__()
        self._calibrations = calibrations or []
        self._filter = ""

    def rowCount(self, parent: QModelIndex | None = None) -> int:
        return len(self._filtered_calibrations())

    def columnCount(self, parent: QModelIndex | None = None) -> int:
        return 10

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return None

        calibration = self._filtered_calibrations()[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 0:
                return calibration.customer.name if calibration.customer is not None else ""
            if index.column() == 1:
                return calibration.study.study_number if calibration.study is not None else ""
            if index.column() == 2:
                return calibration.country.name if calibration.country is not None else ""
            if index.column() == 3:
                return calibration.site.site_number if calibration.site is not None else ""
            if index.column() == 4:
                return calibration.quote.quote_number if calibration.quote is not None else ""
            if index.column() == 5:
                return calibration.device.serial_number if calibration.device is not None else ""
            if index.column() == 6:
                return calibration.supplier.name if calibration.supplier is not None else ""
            if index.column() == 7:
                return calibration.calibration_start_date.strftime("%Y-%m-%d") if calibration.calibration_start_date else ""
            if index.column() == 8:
                return calibration.calibration_due_date.strftime("%Y-%m-%d") if calibration.calibration_due_date else ""
            if index.column() == 9:
                return calibration.status
        return None

    def headerData(self, section: int, orientation: int, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            headers = [
                "Customer",
                "Study",
                "Country",
                "Site",
                "Quote",
                "Device",
                "Supplier",
                "Start Date",
                "Due Date",
                "Status",
            ]
            return headers[section]
        return None

    def set_calibrations(self, calibrations: list[Calibration]) -> None:
        self.beginResetModel()
        self._calibrations = calibrations
        self.endResetModel()

    def set_filter(self, query: str) -> None:
        self.beginResetModel()
        self._filter = query.lower()
        self.endResetModel()

    def calibration_id_at(self, row: int) -> str | None:
        calibrations = self._filtered_calibrations()
        if 0 <= row < len(calibrations):
            return calibrations[row].id
        return None

    def _filtered_calibrations(self) -> list[Calibration]:
        if not self._filter:
            return self._calibrations

        query = self._filter
        return [
            calibration
            for calibration in self._calibrations
            if query in (calibration.customer.name or "").lower()
            or query in (calibration.study.study_number or "").lower()
            or query in (calibration.country.name or "").lower()
            or query in (calibration.site.site_number or "").lower()
            or query in (calibration.quote.quote_number or "").lower()
            or query in (calibration.device.serial_number or "").lower()
            or query in (calibration.supplier.name or "").lower()
            or query in (calibration.status or "").lower()
        ]
