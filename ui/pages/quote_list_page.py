from __future__ import annotations

from typing import Any

from PySide6.QtCore import QModelIndex, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QTableView,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from services.quote_service import QuoteService
from ui.pages.base_page import BasePage
from ui.widgets.quote_form_dialog import QuoteFormDialog
from ui.widgets.quote_table_model import QuoteTableModel


class QuoteListPage(BasePage):
    """Page for managing quotes through the service layer."""

    page_name = "quotes"
    quote_selected = Signal(object)

    def __init__(self, service: QuoteService, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.service = service
        self._selected_quote_id: str | None = None
        self._build_ui()
        self.refresh_quotes()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        header = QLabel("Quote Management")
        header.setStyleSheet("font-size: 22px; font-weight: 600;")
        layout.addWidget(header)

        toolbar = QToolBar("Quote Toolbar")
        toolbar.setMovable(False)
        layout.addWidget(toolbar)

        add_action = QAction("Add Quote", self)
        add_action.triggered.connect(self.add_quote)
        toolbar.addAction(add_action)

        edit_action = QAction("Edit Quote", self)
        edit_action.triggered.connect(self.edit_quote)
        toolbar.addAction(edit_action)

        delete_action = QAction("Delete Quote", self)
        delete_action.triggered.connect(self.delete_selected_quote)
        toolbar.addAction(delete_action)

        refresh_action = QAction("Refresh", self)
        refresh_action.triggered.connect(self.refresh_quotes)
        toolbar.addAction(refresh_action)

        search_container = QWidget(self)
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(8)

        search_label = QLabel("Search:")
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Quote Number, Customer, Study Number, Country, Site")
        self.search_input.textChanged.connect(self._apply_search)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input, 1)
        layout.addWidget(search_container)

        self.table_view = QTableView(self)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_view.setStyleSheet(
            "QTableView { background-color: white; gridline-color: #e5e7eb; }"
            "QTableView::item { padding: 6px; }"
            "QTableView::item:selected { background-color: #dfe9ff; color: #1f2a44; }"
        )
        self.table_view.clicked.connect(self._handle_row_click)
        self.table_view.doubleClicked.connect(self._handle_row_double_click)
        layout.addWidget(self.table_view, 1)

        self.table_model = QuoteTableModel([])
        self.table_view.setModel(self.table_model)
        selection_model = self.table_view.selectionModel()
        if selection_model is not None:
            selection_model.selectionChanged.connect(self._on_selection_changed)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def refresh_quotes(self) -> None:
        selected_quote_id = self._selected_quote_id
        quotes = self.service.get_all()
        self.table_model.set_quotes(quotes)
        self._restore_selection(selected_quote_id)

    def add_quote(self) -> None:
        dialog = QuoteFormDialog(
            self.service.get_customer_options(),
            self.service.study_repository.get_all(),
            self.service.country_repository.get_all(),
            self.service.site_repository.get_all(),
            self,
        )
        if dialog.exec() == QuoteFormDialog.Accepted:
            try:
                sites = [
                    site
                    for site_id in dialog.selected_site_ids()
                    for site in [self.service.site_repository.get_by_id(site_id)]
                    if site is not None
                ]
                self.service.create_quote(
                    quote_number=dialog.quote_number_input.text().strip(),
                    sites=sites,
                    quote_date=dialog.selected_quote_date(),
                    status=dialog.status_combo.currentText(),
                    notes=dialog.notes_input.toPlainText().strip() or None,
                )
                self.refresh_quotes()
            except ValueError as error:
                QMessageBox.warning(self, "Validation Error", str(error))

    def edit_quote(self) -> None:
        if self._selected_quote_id is None:
            QMessageBox.information(self, "Selection Required", "Select a quote to edit.")
            return

        quote = self.service.get_by_id(self._selected_quote_id)
        if quote is None:
            QMessageBox.warning(self, "Not Found", "The selected quote could not be found.")
            return

        dialog = QuoteFormDialog(
            self.service.get_customer_options(),
            self.service.study_repository.get_all(),
            self.service.country_repository.get_all(),
            self.service.site_repository.get_all(),
            self,
        )
        dialog.set_quote(quote)
        if dialog.exec() == QuoteFormDialog.Accepted:
            try:
                sites = [
                    site
                    for site_id in dialog.selected_site_ids()
                    for site in [self.service.site_repository.get_by_id(site_id)]
                    if site is not None
                ]
                self.service.update_quote(
                    quote,
                    quote_number=dialog.quote_number_input.text().strip(),
                    sites=sites,
                    quote_date=dialog.selected_quote_date(),
                    status=dialog.status_combo.currentText(),
                    notes=dialog.notes_input.toPlainText().strip() or None,
                )
                self.refresh_quotes()
            except ValueError as error:
                QMessageBox.warning(self, "Validation Error", str(error))

    def delete_selected_quote(self) -> None:
        if self._selected_quote_id is None:
            QMessageBox.information(self, "Selection Required", "Select a quote to delete.")
            return

        quote = self.service.get_by_id(self._selected_quote_id)
        if quote is None:
            QMessageBox.warning(self, "Not Found", "The selected quote could not be found.")
            return

        confirmation = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete quote {quote.quote_number}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirmation == QMessageBox.StandardButton.Yes:
            self.service.delete_quote(quote)
            self.refresh_quotes()

    def _handle_row_click(self, index: QModelIndex) -> None:
        self._update_selected_quote(index.row())

    def _handle_row_double_click(self, index: Any) -> None:
        self._update_selected_quote(index.row())
        self.edit_quote()

    def _on_selection_changed(self, selected: Any, deselected: Any) -> None:
        if not selected.indexes():
            self._selected_quote_id = None
            self.quote_selected.emit(None)
            return

        self._update_selected_quote(selected.indexes()[0].row())

    def _apply_search(self, query: str) -> None:
        selected_quote_id = self._selected_quote_id
        self.table_model.set_filter(query)
        self._restore_selection(selected_quote_id)

    def _update_selected_quote(self, row: int) -> None:
        self._selected_quote_id = self.table_model.quote_id_at(row)
        self.quote_selected.emit(self._selected_quote_id)

    def _restore_selection(self, quote_id: str | None) -> None:
        self.table_view.clearSelection()
        if quote_id is None:
            self._selected_quote_id = None
            self.quote_selected.emit(None)
            return

        for row in range(self.table_model.rowCount()):
            if self.table_model.quote_id_at(row) == quote_id:
                self.table_view.selectRow(row)
                self._selected_quote_id = quote_id
                self.quote_selected.emit(quote_id)
                return

        self._selected_quote_id = None
        self.quote_selected.emit(None)
