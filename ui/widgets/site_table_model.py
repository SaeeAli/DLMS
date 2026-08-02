from __future__ import annotations

from typing import Any

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from models.site import Site


class SiteTableModel(QAbstractTableModel):
    """Table model for displaying sites in a QTableView."""

    def __init__(self, sites: list[Site] | None = None) -> None:
        super().__init__()
        self._sites = sites or []
        self._filter = ""

    def rowCount(self, parent: QModelIndex | None = None) -> int:
        return len(self._filtered_sites())

    def columnCount(self, parent: QModelIndex | None = None) -> int:
        return 7

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return None

        site = self._filtered_sites()[index.row()]
        assignment = site.study_country
        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 0:
                return assignment.study.customer.name if assignment and assignment.study and assignment.study.customer else ""
            if index.column() == 1:
                return assignment.study.study_number if assignment and assignment.study else ""
            if index.column() == 2:
                return assignment.country.name if assignment and assignment.country else ""
            if index.column() == 3:
                return site.site_number or ""
            if index.column() == 4:
                return site.name or ""
            if index.column() == 5:
                return site.status or ""
            if index.column() == 6:
                return site.created_at.strftime("%Y-%m-%d") if site.created_at else ""
        return None

    def headerData(self, section: int, orientation: int, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            headers = ["Customer", "Study", "Country", "Site Number", "Site Name", "Status", "Created"]
            return headers[section]
        return None

    def set_sites(self, sites: list[Site]) -> None:
        self.beginResetModel()
        self._sites = sites
        self.endResetModel()

    def set_filter(self, query: str) -> None:
        self.beginResetModel()
        self._filter = query.lower()
        self.endResetModel()

    def site_id_at(self, row: int) -> str | None:
        sites = self._filtered_sites()
        if 0 <= row < len(sites):
            return sites[row].id
        return None

    def _filtered_sites(self) -> list[Site]:
        if not self._filter:
            return self._sites

        query = self._filter
        return [
            site
            for site in self._sites
            if query in (site.study_country.study.customer.name or "").lower()
            or query in (site.study_country.study.study_number or "").lower()
            or query in (site.study_country.country.name or "").lower()
            or query in (site.site_number or "").lower()
            or query in (site.name or "").lower()
            or query in (site.status or "").lower()
        ]
