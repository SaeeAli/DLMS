from __future__ import annotations

from typing import Any

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from models.study_country import StudyCountry


class CountryTableModel(QAbstractTableModel):
    """Table model for displaying countries in a QTableView."""

    def __init__(self, countries: list[StudyCountry] | None = None) -> None:
        super().__init__()
        self._countries = countries or []
        self._filter = ""

    def rowCount(self, parent: QModelIndex | None = None) -> int:
        return len(self._filtered_countries())

    def columnCount(self, parent: QModelIndex | None = None) -> int:
        return 5

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return None

        assignment = self._filtered_countries()[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 0:
                return assignment.study.study_number if assignment.study is not None else ""
            if index.column() == 1:
                return assignment.study.customer.name if assignment.study is not None and assignment.study.customer is not None else ""
            if index.column() == 2:
                return assignment.country.name if assignment.country is not None else ""
            if index.column() == 3:
                return assignment.status or ""
            if index.column() == 4:
                return assignment.created_at.strftime("%Y-%m-%d") if assignment.created_at else ""
        return None

    def headerData(self, section: int, orientation: int, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            headers = ["Study Number", "Customer Name", "Country", "Status", "Created Date"]
            return headers[section]
        return None

    def set_countries(self, countries: list[StudyCountry]) -> None:
        self.beginResetModel()
        self._countries = countries
        self.endResetModel()

    def set_filter(self, query: str) -> None:
        self.beginResetModel()
        self._filter = query.lower()
        self.endResetModel()

    def country_id_at(self, row: int) -> str | None:
        countries = self._filtered_countries()
        if 0 <= row < len(countries):
            return countries[row].id
        return None

    def _filtered_countries(self) -> list[StudyCountry]:
        if not self._filter:
            return self._countries

        query = self._filter
        return [
            assignment
            for assignment in self._countries
            if query in (assignment.study.study_number or "").lower()
            or query in (assignment.study.customer.name or "").lower()
            or query in (assignment.country.name or "").lower()
            or query in (assignment.country.country_code or "").lower()
            or query in (assignment.status or "").lower()
        ]
