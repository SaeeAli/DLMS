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

from services.customer_service import CustomerService
from ui.pages.base_page import BasePage
from ui.widgets.customer_form_dialog import CustomerFormDialog
from ui.widgets.customer_table_model import CustomerTableModel


class CustomerListPage(BasePage):
    """Page for managing customers through the service layer."""

    page_name = "customers"
    customer_selected = Signal(object)

    def __init__(self, service: CustomerService, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.service = service
        self._selected_customer_id: str | None = None
        self._build_ui()
        self.refresh_customers()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        header = QLabel("Customer Management")
        header.setStyleSheet("font-size: 22px; font-weight: 600;")
        layout.addWidget(header)

        toolbar = QToolBar("Customer Toolbar")
        toolbar.setMovable(False)
        layout.addWidget(toolbar)

        add_action = QAction("Add Customer", self)
        add_action.triggered.connect(self.add_customer)
        toolbar.addAction(add_action)

        edit_action = QAction("Edit Customer", self)
        edit_action.triggered.connect(self.edit_customer)
        toolbar.addAction(edit_action)

        delete_action = QAction("Delete Customer", self)
        delete_action.triggered.connect(self.delete_selected_customer)
        toolbar.addAction(delete_action)

        refresh_action = QAction("Refresh", self)
        refresh_action.triggered.connect(self.refresh_customers)
        toolbar.addAction(refresh_action)

        search_container = QWidget(self)
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(8)

        search_label = QLabel("Search:")
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Customer Name, Email")
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

        self.table_model = CustomerTableModel([])
        self.table_view.setModel(self.table_model)
        selection_model = self.table_view.selectionModel()
        if selection_model is not None:
            selection_model.selectionChanged.connect(self._on_selection_changed)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def refresh_customers(self) -> None:
        selected_customer_id = self._selected_customer_id
        customers = self.service.get_all()
        self.table_model.set_customers(customers)
        self._restore_selection(selected_customer_id)

    def add_customer(self) -> None:
        dialog = CustomerFormDialog(self)
        if dialog.exec() == CustomerFormDialog.Accepted:
            try:
                self.service.create_customer(
                    name=dialog.name_input.text().strip(),
                    contact_email=dialog.contact_email_input.text().strip() or None,
                )
                self.refresh_customers()
            except ValueError as error:
                QMessageBox.warning(self, "Validation Error", str(error))

    def edit_customer(self) -> None:
        if self._selected_customer_id is None:
            QMessageBox.information(self, "Selection Required", "Select a customer to edit.")
            return

        customer = self.service.get_by_id(self._selected_customer_id)
        if customer is None:
            QMessageBox.warning(self, "Not Found", "The selected customer could not be found.")
            return

        dialog = CustomerFormDialog(self)
        dialog.set_customer(customer)
        if dialog.exec() == CustomerFormDialog.Accepted:
            try:
                self.service.update_customer(
                    customer,
                    name=dialog.name_input.text().strip(),
                    contact_email=dialog.contact_email_input.text().strip() or None,
                )
                self.refresh_customers()
            except ValueError as error:
                QMessageBox.warning(self, "Validation Error", str(error))

    def delete_selected_customer(self) -> None:
        if self._selected_customer_id is None:
            QMessageBox.information(self, "Selection Required", "Select a customer to delete.")
            return

        customer = self.service.get_by_id(self._selected_customer_id)
        if customer is None:
            QMessageBox.warning(self, "Not Found", "The selected customer could not be found.")
            return

        confirmation = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete customer {customer.name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirmation == QMessageBox.StandardButton.Yes:
            self.service.delete_customer(customer)
            self.refresh_customers()

    def _handle_row_click(self, index: QModelIndex) -> None:
        self._update_selected_customer(index.row())

    def _handle_row_double_click(self, index: Any) -> None:
        self._update_selected_customer(index.row())
        self.edit_customer()

    def _on_selection_changed(self, selected: Any, deselected: Any) -> None:
        if not selected.indexes():
            self._selected_customer_id = None
            self.customer_selected.emit(None)
            return

        self._update_selected_customer(selected.indexes()[0].row())

    def _apply_search(self, query: str) -> None:
        selected_customer_id = self._selected_customer_id
        self.table_model.set_filter(query)
        self._restore_selection(selected_customer_id)

    def _clear_selection(self) -> None:
        self.table_view.clearSelection()
        self._selected_customer_id = None
        self.customer_selected.emit(None)

    def _update_selected_customer(self, row: int) -> None:
        self._selected_customer_id = self.table_model.customer_id_at(row)
        self.customer_selected.emit(self._selected_customer_id)

    def _restore_selection(self, customer_id: str | None) -> None:
        self.table_view.clearSelection()
        if customer_id is None:
            self._selected_customer_id = None
            self.customer_selected.emit(None)
            return

        for row in range(self.table_model.rowCount()):
            if self.table_model.customer_id_at(row) == customer_id:
                self.table_view.selectRow(row)
                self._selected_customer_id = customer_id
                self.customer_selected.emit(customer_id)
                return

        self._selected_customer_id = None
        self.customer_selected.emit(None)
