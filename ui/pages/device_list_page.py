from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt, Signal
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

from models.device import Device
from services.device_service import DeviceService
from ui.pages.base_page import BasePage
from ui.widgets.device_table_model import DeviceTableModel
from ui.widgets.device_form_dialog import DeviceFormDialog


class DeviceListPage(BasePage):
    """Page for managing devices through the service layer."""

    page_name = "devices"
    device_selected = Signal(str | None)

    def __init__(self, service: DeviceService, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.service = service
        self._selected_device_id: str | None = None
        self._build_ui()
        self.refresh_devices()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        header = QLabel("Device Management")
        header.setStyleSheet("font-size: 22px; font-weight: 600;")
        layout.addWidget(header)

        toolbar = QToolBar("Device Toolbar")
        toolbar.setMovable(False)
        layout.addWidget(toolbar)

        add_action = QAction("Add Device", self)
        add_action.triggered.connect(self.add_device)
        toolbar.addAction(add_action)

        edit_action = QAction("Edit Device", self)
        edit_action.triggered.connect(self.edit_device)
        toolbar.addAction(edit_action)

        delete_action = QAction("Delete Device", self)
        delete_action.triggered.connect(self.delete_selected_device)
        toolbar.addAction(delete_action)

        refresh_action = QAction("Refresh", self)
        refresh_action.triggered.connect(self.refresh_devices)
        toolbar.addAction(refresh_action)

        search_container = QWidget(self)
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(8)

        search_label = QLabel("Search:")
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Brand, Type of Device, Model, Serial Number")
        self.search_input.textChanged.connect(self._apply_search)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input, 1)
        layout.addWidget(search_container)

        self.table_view = QTableView(self)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_view.doubleClicked.connect(self._handle_row_double_click)
        layout.addWidget(self.table_view, 1)

        self.table_model = DeviceTableModel([])
        self.table_view.setModel(self.table_model)
        selection_model = self.table_view.selectionModel()
        if selection_model is not None:
            selection_model.selectionChanged.connect(self._on_selection_changed)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def refresh_devices(self) -> None:
        devices = self.service.get_all()
        self.table_model.set_devices(devices)
        self._clear_selection()

    def add_device(self) -> None:
        dialog = DeviceFormDialog(self, device_type_options=self.service.get_device_type_options())
        if dialog.exec() == DeviceFormDialog.Accepted:
            try:
                self.service.create_device(
                    brand=dialog.brand_input.text().strip(),
                    device_type=dialog.device_type_combo.currentText().strip(),
                    model=dialog.model_input.text().strip() or None,
                    serial_number=dialog.serial_number_input.text().strip() or None,
                )
                self.refresh_devices()
            except ValueError as error:
                QMessageBox.warning(self, "Validation Error", str(error))

    def edit_device(self) -> None:
        if self._selected_device_id is None:
            QMessageBox.information(self, "Selection Required", "Select a device to edit.")
            return

        device = self.service.get_by_id(self._selected_device_id)
        if device is None:
            QMessageBox.warning(self, "Not Found", "The selected device could not be found.")
            return

        dialog = DeviceFormDialog(self, device_type_options=self.service.get_device_type_options())
        dialog.set_device(device)
        if dialog.exec() == DeviceFormDialog.Accepted:
            try:
                self.service.update_device(
                    device,
                    brand=dialog.brand_input.text().strip(),
                    device_type=dialog.device_type_combo.currentText().strip(),
                    model=dialog.model_input.text().strip() or None,
                    serial_number=dialog.serial_number_input.text().strip() or None,
                )
                self.refresh_devices()
            except ValueError as error:
                QMessageBox.warning(self, "Validation Error", str(error))

    def delete_selected_device(self) -> None:
        if self._selected_device_id is None:
            QMessageBox.information(self, "Selection Required", "Select a device to delete.")
            return

        device = self.service.get_by_id(self._selected_device_id)
        if device is None:
            QMessageBox.warning(self, "Not Found", "The selected device could not be found.")
            return

        confirmation = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete device {device.brand or device.asset_tag}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirmation == QMessageBox.StandardButton.Yes:
            self.service.delete_device(device)
            self.refresh_devices()

    def _handle_row_double_click(self, index: Any) -> None:
        self._selected_device_id = self.table_model.device_id_at(index.row())
        self.device_selected.emit(self._selected_device_id)
        self.edit_device()

    def _on_selection_changed(self, selected: Any, deselected: Any) -> None:
        if not selected.indexes():
            self._selected_device_id = None
            return

        row = selected.indexes()[0].row()
        self._selected_device_id = self.table_model.device_id_at(row)
        self.device_selected.emit(self._selected_device_id)

    def _apply_search(self, query: str) -> None:
        self.table_model.set_filter(query)

    def _clear_selection(self) -> None:
        self.table_view.clearSelection()
        self._selected_device_id = None
