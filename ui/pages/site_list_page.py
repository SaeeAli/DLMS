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

from services.site_service import SiteService
from ui.pages.base_page import BasePage
from ui.widgets.site_form_dialog import SiteFormDialog
from ui.widgets.site_table_model import SiteTableModel


class SiteListPage(BasePage):
    """Page for managing sites through the service layer."""

    page_name = "sites"
    site_selected = Signal(object)

    def __init__(self, service: SiteService, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.service = service
        self._selected_site_id: str | None = None
        self._build_ui()
        self.refresh_sites()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        header = QLabel("Site Management")
        header.setStyleSheet("font-size: 22px; font-weight: 600;")
        layout.addWidget(header)

        toolbar = QToolBar("Site Toolbar")
        toolbar.setMovable(False)
        layout.addWidget(toolbar)

        add_action = QAction("Add Site", self)
        add_action.triggered.connect(self.add_site)
        toolbar.addAction(add_action)

        edit_action = QAction("Edit Site", self)
        edit_action.triggered.connect(self.edit_site)
        toolbar.addAction(edit_action)

        delete_action = QAction("Delete Site", self)
        delete_action.triggered.connect(self.delete_selected_site)
        toolbar.addAction(delete_action)

        refresh_action = QAction("Refresh", self)
        refresh_action.triggered.connect(self.refresh_sites)
        toolbar.addAction(refresh_action)

        search_container = QWidget(self)
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(8)

        search_label = QLabel("Search:")
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Customer, Study, Country, Site Number, Site Name")
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

        self.table_model = SiteTableModel([])
        self.table_view.setModel(self.table_model)
        selection_model = self.table_view.selectionModel()
        if selection_model is not None:
            selection_model.selectionChanged.connect(self._on_selection_changed)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def refresh_sites(self) -> None:
        selected_site_id = self._selected_site_id
        sites = self.service.get_all()
        self.table_model.set_sites(sites)
        self._restore_selection(selected_site_id)

    def add_site(self) -> None:
        dialog = SiteFormDialog(self.service.get_study_country_options(), self)
        if dialog.exec() == SiteFormDialog.Accepted:
            try:
                assignment = self.service.study_country_repository.get_by_id(dialog.selected_study_country_id() or "")
                self.service.create_site(
                    study_country=assignment,
                    site_number=dialog.site_number_input.text().strip(),
                    name=dialog.name_input.text().strip(),
                    address=dialog.address_input.text().strip() or None,
                    city=dialog.city_input.text().strip() or None,
                    status=dialog.status_combo.currentText(),
                    notes=dialog.notes_input.toPlainText().strip() or None,
                )
                self.refresh_sites()
            except ValueError as error:
                QMessageBox.warning(self, "Validation Error", str(error))

    def edit_site(self) -> None:
        if self._selected_site_id is None:
            QMessageBox.information(self, "Selection Required", "Select a site to edit.")
            return

        site = self.service.get_by_id(self._selected_site_id)
        if site is None:
            QMessageBox.warning(self, "Not Found", "The selected site could not be found.")
            return

        dialog = SiteFormDialog(self.service.get_study_country_options(), self)
        dialog.set_site(site)
        if dialog.exec() == SiteFormDialog.Accepted:
            try:
                assignment = self.service.study_country_repository.get_by_id(dialog.selected_study_country_id() or "")
                self.service.update_site(
                    site,
                    study_country=assignment,
                    site_number=dialog.site_number_input.text().strip(),
                    name=dialog.name_input.text().strip(),
                    address=dialog.address_input.text().strip() or None,
                    city=dialog.city_input.text().strip() or None,
                    status=dialog.status_combo.currentText(),
                    notes=dialog.notes_input.toPlainText().strip() or None,
                )
                self.refresh_sites()
            except ValueError as error:
                QMessageBox.warning(self, "Validation Error", str(error))

    def delete_selected_site(self) -> None:
        if self._selected_site_id is None:
            QMessageBox.information(self, "Selection Required", "Select a site to delete.")
            return

        site = self.service.get_by_id(self._selected_site_id)
        if site is None:
            QMessageBox.warning(self, "Not Found", "The selected site could not be found.")
            return

        confirmation = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete site {site.site_number}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirmation == QMessageBox.StandardButton.Yes:
            self.service.delete_site(site)
            self.refresh_sites()

    def _handle_row_click(self, index: QModelIndex) -> None:
        self._update_selected_site(index.row())

    def _handle_row_double_click(self, index: Any) -> None:
        self._update_selected_site(index.row())
        self.edit_site()

    def _on_selection_changed(self, selected: Any, deselected: Any) -> None:
        if not selected.indexes():
            self._selected_site_id = None
            self.site_selected.emit(None)
            return

        self._update_selected_site(selected.indexes()[0].row())

    def _apply_search(self, query: str) -> None:
        selected_site_id = self._selected_site_id
        self.table_model.set_filter(query)
        self._restore_selection(selected_site_id)

    def _update_selected_site(self, row: int) -> None:
        self._selected_site_id = self.table_model.site_id_at(row)
        self.site_selected.emit(self._selected_site_id)

    def _restore_selection(self, site_id: str | None) -> None:
        self.table_view.clearSelection()
        if site_id is None:
            self._selected_site_id = None
            self.site_selected.emit(None)
            return

        for row in range(self.table_model.rowCount()):
            if self.table_model.site_id_at(row) == site_id:
                self.table_view.selectRow(row)
                self._selected_site_id = site_id
                self.site_selected.emit(site_id)
                return

        self._selected_site_id = None
        self.site_selected.emit(None)
