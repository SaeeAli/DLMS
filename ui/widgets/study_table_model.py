from __future__ import annotations

from typing import Any

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from models.study import Study


class StudyTableModel(QAbstractTableModel):
    """Table model for displaying studies in a QTableView."""

    def __init__(self, studies: list[Study] | None = None) -> None:
        super().__init__()
        self._studies = studies or []
        self._filter = ""

    def rowCount(self, parent: QModelIndex | None = None) -> int:
        return len(self._filtered_studies())

    def columnCount(self, parent: QModelIndex | None = None) -> int:
        return 4

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return None

        study = self._filtered_studies()[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 0:
                return study.customer.name if study.customer is not None else ""
            if index.column() == 1:
                return study.study_number or ""
            if index.column() == 2:
                return study.status or ""
            if index.column() == 3:
                return study.created_at.strftime("%Y-%m-%d") if study.created_at else ""
        return None

    def headerData(self, section: int, orientation: int, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            headers = ["Customer Name", "Study Number", "Status", "Created Date"]
            return headers[section]
        return None

    def set_studies(self, studies: list[Study]) -> None:
        self.beginResetModel()
        self._studies = studies
        self.endResetModel()

    def set_filter(self, query: str) -> None:
        self.beginResetModel()
        self._filter = query.lower()
        self.endResetModel()

    def study_id_at(self, row: int) -> str | None:
        studies = self._filtered_studies()
        if 0 <= row < len(studies):
            return studies[row].id
        return None

    def _filtered_studies(self) -> list[Study]:
        if not self._filter:
            return self._studies

        query = self._filter
        return [
            study
            for study in self._studies
            if query in (study.customer.name or "").lower()
            or query in (study.study_number or "").lower()
            or query in (study.status or "").lower()
        ]
