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

from services.supplier_service import SupplierService
from ui.pages.base_page import BasePage
from ui.widgets.supplier_form_dialog import SupplierFormDialog
from ui.widgets.supplier_table_model import SupplierTableModel


class SupplierListPage(BasePage):
    """Page for managing suppliers through the service layer."""

    page_name = "suppliers"
    supplier_selected = Signal(object)

    def __init__(self, service: SupplierService, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.service = service
        self._selected_supplier_id: str | None = None
        self._build_ui()
        self.refresh_suppliers()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        header = QLabel("Supplier Management")
        header.setStyleSheet("font-size: 22px; font-weight: 600;")
        layout.addWidget(header)

        toolbar = QToolBar("Supplier Toolbar")
        toolbar.setMovable(False)
        layout.addWidget(toolbar)

        add_action = QAction("Add Supplier", self)
        add_action.triggered.connect(self.add_supplier)
        toolbar.addAction(add_action)

        edit_action = QAction("Edit Supplier", self)
        edit_action.triggered.connect(self.edit_supplier)
        toolbar.addAction(edit_action)

        delete_action = QAction("Delete Supplier", self)
        delete_action.triggered.connect(self.delete_selected_supplier)
        toolbar.addAction(delete_action)

        refresh_action = QAction("Refresh", self)
        refresh_action.triggered.connect(self.refresh_suppliers)
        toolbar.addAction(refresh_action)

        search_container = QWidget(self)
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(8)

        search_label = QLabel("Search:")
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Supplier Name, Country, Contact Person")
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

        self.table_model = SupplierTableModel([])
        self.table_view.setModel(self.table_model)
        selection_model = self.table_view.selectionModel()
        if selection_model is not None:
            selection_model.selectionChanged.connect(self._on_selection_changed)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def refresh_suppliers(self) -> None:
        selected_supplier_id = self._selected_supplier_id
        suppliers = self.service.get_all()
        self.table_model.set_suppliers(suppliers)
        self._restore_selection(selected_supplier_id)

    def add_supplier(self) -> None:
        dialog = SupplierFormDialog(self.service.get_currency_options(), self)
        if dialog.exec() == SupplierFormDialog.Accepted:
            try:
                self.service.create_supplier(
                    name=dialog.name_input.text().strip(),
                    country=dialog.country_input.text().strip() or None,
                    city=dialog.city_input.text().strip() or None,
                    address=dialog.address_input.text().strip() or None,
                    contact_person=dialog.contact_person_input.text().strip() or None,
                    email=dialog.email_input.text().strip() or None,
                    phone=dialog.phone_input.text().strip() or None,
                    on_site_calibration=dialog.on_site_calibration_value(),
                    exchange_device_available=dialog.exchange_device_available_value(),
                    shipping_supported=dialog.shipping_supported_value(),
                    currency=dialog.currency_combo.currentText(),
                    default_calibration_lead_time_days=dialog.default_calibration_lead_time_days_input.value(),
                )
                self.refresh_suppliers()
            except ValueError as error:
                QMessageBox.warning(self, "Validation Error", str(error))

    def edit_supplier(self) -> None:
        if self._selected_supplier_id is None:
            QMessageBox.information(self, "Selection Required", "Select a supplier to edit.")
            return

        supplier = self.service.get_by_id(self._selected_supplier_id)
        if supplier is None:
            QMessageBox.warning(self, "Not Found", "The selected supplier could not be found.")
            return

        dialog = SupplierFormDialog(self.service.get_currency_options(), self)
        dialog.set_supplier(supplier)
        if dialog.exec() == SupplierFormDialog.Accepted:
            try:
                self.service.update_supplier(
                    supplier,
                    name=dialog.name_input.text().strip(),
                    country=dialog.country_input.text().strip() or None,
                    city=dialog.city_input.text().strip() or None,
                    address=dialog.address_input.text().strip() or None,
                    contact_person=dialog.contact_person_input.text().strip() or None,
                    email=dialog.email_input.text().strip() or None,
                    phone=dialog.phone_input.text().strip() or None,
                    on_site_calibration=dialog.on_site_calibration_value(),
                    exchange_device_available=dialog.exchange_device_available_value(),
                    shipping_supported=dialog.shipping_supported_value(),
                    currency=dialog.currency_combo.currentText(),
                    default_calibration_lead_time_days=dialog.default_calibration_lead_time_days_input.value(),
                )
                self.refresh_suppliers()
            except ValueError as error:
                QMessageBox.warning(self, "Validation Error", str(error))

    def delete_selected_supplier(self) -> None:
        if self._selected_supplier_id is None:
            QMessageBox.information(self, "Selection Required", "Select a supplier to delete.")
            return

        supplier = self.service.get_by_id(self._selected_supplier_id)
        if supplier is None:
            QMessageBox.warning(self, "Not Found", "The selected supplier could not be found.")
            return

        confirmation = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete supplier {supplier.name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirmation == QMessageBox.StandardButton.Yes:
            self.service.delete_supplier(supplier)
            self.refresh_suppliers()

    def _handle_row_click(self, index: QModelIndex) -> None:
        self._update_selected_supplier(index.row())

    def _handle_row_double_click(self, index: Any) -> None:
        self._update_selected_supplier(index.row())
        self.edit_supplier()

    def _on_selection_changed(self, selected: Any, deselected: Any) -> None:
        if not selected.indexes():
            self._selected_supplier_id = None
            self.supplier_selected.emit(None)
            return

        self._update_selected_supplier(selected.indexes()[0].row())

    def _apply_search(self, query: str) -> None:
        selected_supplier_id = self._selected_supplier_id
        self.table_model.set_filter(query)
        self._restore_selection(selected_supplier_id)

    def _update_selected_supplier(self, row: int) -> None:
        self._selected_supplier_id = self.table_model.supplier_id_at(row)
        self.supplier_selected.emit(self._selected_supplier_id)

    def _restore_selection(self, supplier_id: str | None) -> None:
        self.table_view.clearSelection()
        if supplier_id is None:
            self._selected_supplier_id = None
            self.supplier_selected.emit(None)
            return

        for row in range(self.table_model.rowCount()):
            if self.table_model.supplier_id_at(row) == supplier_id:
                self.table_view.selectRow(row)
                self._selected_supplier_id = supplier_id
                self.supplier_selected.emit(supplier_id)
                return

        self._selected_supplier_id = None
        self.supplier_selected.emit(None)
