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

from services.country_service import CountryService
from ui.pages.base_page import BasePage
from ui.widgets.country_form_dialog import CountryFormDialog
from ui.widgets.country_table_model import CountryTableModel


class CountryListPage(BasePage):
    """Page for managing country and site records through the service layer."""

    page_name = "countries"
    country_selected = Signal(object)

    def __init__(self, service: CountryService, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.service = service
        self._selected_country_id: str | None = None
        self._build_ui()
        self.refresh_countries()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        header = QLabel("Country Management")
        header.setStyleSheet("font-size: 22px; font-weight: 600;")
        layout.addWidget(header)

        toolbar = QToolBar("Country Toolbar")
        toolbar.setMovable(False)
        layout.addWidget(toolbar)

        add_action = QAction("Add Country", self)
        add_action.triggered.connect(self.add_country)
        toolbar.addAction(add_action)

        edit_action = QAction("Edit Country", self)
        edit_action.triggered.connect(self.edit_country)
        toolbar.addAction(edit_action)

        delete_action = QAction("Delete Country", self)
        delete_action.triggered.connect(self.delete_selected_country)
        toolbar.addAction(delete_action)

        refresh_action = QAction("Refresh", self)
        refresh_action.triggered.connect(self.refresh_countries)
        toolbar.addAction(refresh_action)

        search_container = QWidget(self)
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(8)

        search_label = QLabel("Search:")
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Study, Country, Site Number, Status")
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

        self.table_model = CountryTableModel([])
        self.table_view.setModel(self.table_model)
        selection_model = self.table_view.selectionModel()
        if selection_model is not None:
            selection_model.selectionChanged.connect(self._on_selection_changed)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def refresh_countries(self) -> None:
        selected_country_id = self._selected_country_id
        countries = self.service.get_country_records()
        self.table_model.set_countries(countries)
        self._restore_selection(selected_country_id)

    def add_country(self) -> None:
        dialog = CountryFormDialog(self.service.get_customer_options(), self.service.get_study_options(), self)
        if dialog.exec() == CountryFormDialog.Accepted:
            try:
                customer_id = dialog.selected_customer_id()
                study = self.service.study_repository.get_by_id(dialog.selected_study_id() or "")
                if customer_id is None:
                    raise ValueError("customer is required")
                if study is None or study.customer_id != customer_id:
                    raise ValueError("study is required")
                self.service.create_country_record(
                    study=study,
                    country_name=dialog.country_input.text().strip(),
                    site_number=dialog.site_number_input.text().strip(),
                    status=dialog.status_combo.currentText(),
                    notes=dialog.notes_input.toPlainText().strip() or None,
                )
                self.refresh_countries()
            except ValueError as error:
                QMessageBox.warning(self, "Validation Error", str(error))

    def edit_country(self) -> None:
        if self._selected_country_id is None:
            QMessageBox.information(self, "Selection Required", "Select a country to edit.")
            return

        country = self.service.get_country_record_by_id(self._selected_country_id)
        if country is None:
            QMessageBox.warning(self, "Not Found", "The selected country could not be found.")
            return

        dialog = CountryFormDialog(self.service.get_customer_options(), self.service.get_study_options(), self)
        dialog.set_country(country)
        if dialog.exec() == CountryFormDialog.Accepted:
            try:
                customer_id = dialog.selected_customer_id()
                study = self.service.study_repository.get_by_id(dialog.selected_study_id() or "")
                if customer_id is None:
                    raise ValueError("customer is required")
                if study is None or study.customer_id != customer_id:
                    raise ValueError("study is required")
                self.service.update_country_record(
                    country,
                    study=study,
                    country_name=dialog.country_input.text().strip(),
                    site_number=dialog.site_number_input.text().strip(),
                    status=dialog.status_combo.currentText(),
                    notes=dialog.notes_input.toPlainText().strip() or None,
                )
                self.refresh_countries()
            except ValueError as error:
                QMessageBox.warning(self, "Validation Error", str(error))

    def delete_selected_country(self) -> None:
        if self._selected_country_id is None:
            QMessageBox.information(self, "Selection Required", "Select a country to delete.")
            return

        country = self.service.get_country_record_by_id(self._selected_country_id)
        if country is None:
            QMessageBox.warning(self, "Not Found", "The selected country could not be found.")
            return

        confirmation = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete site {country.site_number} from country management?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirmation == QMessageBox.StandardButton.Yes:
            try:
                self.service.delete_country_record(country)
                self.refresh_countries()
            except ValueError as error:
                QMessageBox.warning(self, "Delete Not Allowed", str(error))

    def _handle_row_click(self, index: QModelIndex) -> None:
        self._update_selected_country(index.row())

    def _handle_row_double_click(self, index: Any) -> None:
        self._update_selected_country(index.row())
        self.edit_country()

    def _on_selection_changed(self, selected: Any, deselected: Any) -> None:
        if not selected.indexes():
            self._selected_country_id = None
            self.country_selected.emit(None)
            return

        self._update_selected_country(selected.indexes()[0].row())

    def _apply_search(self, query: str) -> None:
        selected_country_id = self._selected_country_id
        self.table_model.set_filter(query)
        self._restore_selection(selected_country_id)

    def _update_selected_country(self, row: int) -> None:
        self._selected_country_id = self.table_model.country_id_at(row)
        self.country_selected.emit(self._selected_country_id)

    def _restore_selection(self, country_id: str | None) -> None:
        self.table_view.clearSelection()
        if country_id is None:
            self._selected_country_id = None
            self.country_selected.emit(None)
            return

        for row in range(self.table_model.rowCount()):
            if self.table_model.country_id_at(row) == country_id:
                self.table_view.selectRow(row)
                self._selected_country_id = country_id
                self.country_selected.emit(country_id)
                return

        self._selected_country_id = None
        self.country_selected.emit(None)
