from __future__ import annotations

from typing import Any

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from models.quote import Quote


class QuoteTableModel(QAbstractTableModel):
    """Table model for displaying quotes in a QTableView."""

    def __init__(self, quotes: list[Quote] | None = None) -> None:
        super().__init__()
        self._quotes = quotes or []
        self._filter = ""

    def rowCount(self, parent: QModelIndex | None = None) -> int:
        return len(self._filtered_quotes())

    def columnCount(self, parent: QModelIndex | None = None) -> int:
        return 7

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return None

        quote = self._filtered_quotes()[index.row()]
        site = quote.site
        assignment = site.study_country if site is not None else None
        study = assignment.study if assignment is not None else None
        country = assignment.country if assignment is not None else None

        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 0:
                return quote.quote_number or ""
            if index.column() == 1:
                return study.customer.name if study is not None and study.customer is not None else ""
            if index.column() == 2:
                return study.study_number if study is not None else ""
            if index.column() == 3:
                return country.name if country is not None else ""
            if index.column() == 4:
                return site.site_number if site is not None else ""
            if index.column() == 5:
                return quote.quote_date.strftime("%Y-%m-%d") if quote.quote_date else ""
            if index.column() == 6:
                return quote.status or ""
        return None

    def headerData(self, section: int, orientation: int, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            headers = ["Quote Number", "Customer", "Study", "Country", "Site", "Quote Date", "Status"]
            return headers[section]
        return None

    def set_quotes(self, quotes: list[Quote]) -> None:
        self.beginResetModel()
        self._quotes = quotes
        self.endResetModel()

    def set_filter(self, query: str) -> None:
        self.beginResetModel()
        self._filter = query.lower()
        self.endResetModel()

    def quote_id_at(self, row: int) -> str | None:
        quotes = self._filtered_quotes()
        if 0 <= row < len(quotes):
            return quotes[row].id
        return None

    def _filtered_quotes(self) -> list[Quote]:
        if not self._filter:
            return self._quotes

        query = self._filter
        return [
            quote
            for quote in self._quotes
            if query in (quote.quote_number or "").lower()
            or query in (quote.site.study_country.study.customer.name or "").lower()
            or query in (quote.site.study_country.study.study_number or "").lower()
            or query in (quote.site.study_country.country.name or "").lower()
            or query in (quote.site.site_number or "").lower()
            or query in (quote.status or "").lower()
        ]
