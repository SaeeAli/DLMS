from __future__ import annotations

from typing import Any

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from models.site import Site


class CountryTableModel(QAbstractTableModel):
    """Table model for displaying countries in a QTableView."""

    def __init__(self, countries: list[Site] | None = None) -> None:
        super().__init__()
        self._countries = countries or []
        self._filter = ""

    def rowCount(self, parent: QModelIndex | None = None) -> int:
        return len(self._filtered_countries())

    def columnCount(self, parent: QModelIndex | None = None) -> int:
        return 4

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return None

        site = self._filtered_countries()[index.row()]
        assignment = site.study_country
        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 0:
                return assignment.study.study_number if assignment and assignment.study is not None else ""
            if index.column() == 1:
                return assignment.country.name if assignment and assignment.country is not None else ""
            if index.column() == 2:
                return site.site_number or ""
            if index.column() == 3:
                return site.status or ""
        return None

    def headerData(self, section: int, orientation: int, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            headers = ["Study", "Country", "Site Number", "Status"]
            return headers[section]
        return None

    def set_countries(self, countries: list[Site]) -> None:
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

    def _filtered_countries(self) -> list[Site]:
        if not self._filter:
            return self._countries

        query = self._filter
        return [
            site
            for site in self._countries
            if query in (site.study_country.study.study_number or "").lower()
            or query in (site.study_country.country.name or "").lower()
            or query in (site.site_number or "").lower()
            or query in (site.status or "").lower()
        ]
