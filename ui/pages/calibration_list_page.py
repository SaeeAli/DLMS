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

from services.calibration_service import CalibrationService
from ui.pages.base_page import BasePage
from ui.widgets.calibration_form_dialog import CalibrationFormDialog
from ui.widgets.calibration_table_model import CalibrationTableModel


class CalibrationListPage(BasePage):
    """Page for managing calibration records through the service layer."""

    page_name = "calibrations"
    calibration_selected = Signal(object)

    def __init__(self, service: CalibrationService, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.service = service
        self._selected_calibration_id: str | None = None
        self._build_ui()
        self.refresh_calibrations()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        header = QLabel("Calibration Management")
        header.setStyleSheet("font-size: 22px; font-weight: 600;")
        layout.addWidget(header)

        toolbar = QToolBar("Calibration Toolbar")
        toolbar.setMovable(False)
        layout.addWidget(toolbar)

        add_action = QAction("Add Calibration", self)
        add_action.triggered.connect(self.add_calibration)
        toolbar.addAction(add_action)

        edit_action = QAction("Edit Calibration", self)
        edit_action.triggered.connect(self.edit_calibration)
        toolbar.addAction(edit_action)

        delete_action = QAction("Delete Calibration", self)
        delete_action.triggered.connect(self.delete_selected_calibration)
        toolbar.addAction(delete_action)

        refresh_action = QAction("Refresh", self)
        refresh_action.triggered.connect(self.refresh_calibrations)
        toolbar.addAction(refresh_action)

        search_container = QWidget(self)
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(8)

        search_label = QLabel("Search:")
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Customer, Study, Country, Site, Quote, Device, Supplier, Status")
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

        self.table_model = CalibrationTableModel([])
        self.table_view.setModel(self.table_model)
        selection_model = self.table_view.selectionModel()
        if selection_model is not None:
            selection_model.selectionChanged.connect(self._on_selection_changed)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def refresh_calibrations(self) -> None:
        selected_calibration_id = self._selected_calibration_id
        calibrations = self.service.get_all()
        self.table_model.set_calibrations(calibrations)
        self._restore_selection(selected_calibration_id)

    def add_calibration(self) -> None:
        dialog = self._build_dialog()
        if dialog.exec() == CalibrationFormDialog.Accepted:
            try:
                self.service.create_calibration(
                    customer_id=dialog.selected_customer_id() or "",
                    study_id=dialog.selected_study_id() or "",
                    country_id=dialog.selected_country_id() or "",
                    site_id=dialog.selected_site_id() or "",
                    quote_id=dialog.selected_quote_id() or "",
                    device_id=dialog.selected_device_id() or "",
                    supplier_id=dialog.selected_supplier_id() or "",
                    calibration_start_date=dialog.selected_calibration_start_date(),
                    calibration_cycle_months=dialog.calibration_cycle_months_input.value(),
                    calibration_due_date=dialog.selected_calibration_due_date(),
                    outbound_tracking_number=dialog.outbound_tracking_number_input.text().strip() or None,
                    delivery_date=dialog.selected_delivery_date(),
                    delivery_confirmed=dialog.delivery_confirmed_input.isChecked(),
                    return_tracking_number=dialog.return_tracking_number_input.text().strip() or None,
                    return_received_date=dialog.selected_return_received_date(),
                    status=dialog.status_combo.currentText(),
                )
                self.refresh_calibrations()
            except ValueError as error:
                QMessageBox.warning(self, "Validation Error", str(error))

    def edit_calibration(self) -> None:
        if self._selected_calibration_id is None:
            QMessageBox.information(self, "Selection Required", "Select a calibration to edit.")
            return

        calibration = self.service.get_by_id(self._selected_calibration_id)
        if calibration is None:
            QMessageBox.warning(self, "Not Found", "The selected calibration could not be found.")
            return

        dialog = self._build_dialog()
        dialog.set_calibration(calibration)
        if dialog.exec() == CalibrationFormDialog.Accepted:
            try:
                self.service.update_calibration(
                    calibration,
                    customer_id=dialog.selected_customer_id() or "",
                    study_id=dialog.selected_study_id() or "",
                    country_id=dialog.selected_country_id() or "",
                    site_id=dialog.selected_site_id() or "",
                    quote_id=dialog.selected_quote_id() or "",
                    device_id=dialog.selected_device_id() or "",
                    supplier_id=dialog.selected_supplier_id() or "",
                    calibration_start_date=dialog.selected_calibration_start_date(),
                    calibration_cycle_months=dialog.calibration_cycle_months_input.value(),
                    calibration_due_date=dialog.selected_calibration_due_date(),
                    outbound_tracking_number=dialog.outbound_tracking_number_input.text().strip() or None,
                    delivery_date=dialog.selected_delivery_date(),
                    delivery_confirmed=dialog.delivery_confirmed_input.isChecked(),
                    return_tracking_number=dialog.return_tracking_number_input.text().strip() or None,
                    return_received_date=dialog.selected_return_received_date(),
                    status=dialog.status_combo.currentText(),
                )
                self.refresh_calibrations()
            except ValueError as error:
                QMessageBox.warning(self, "Validation Error", str(error))

    def delete_selected_calibration(self) -> None:
        if self._selected_calibration_id is None:
            QMessageBox.information(self, "Selection Required", "Select a calibration to delete.")
            return

        calibration = self.service.get_by_id(self._selected_calibration_id)
        if calibration is None:
            QMessageBox.warning(self, "Not Found", "The selected calibration could not be found.")
            return

        confirmation = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete calibration for device {calibration.device.serial_number if calibration.device is not None else ''}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirmation == QMessageBox.StandardButton.Yes:
            self.service.delete_calibration(calibration)
            self.refresh_calibrations()

    def _build_dialog(self) -> CalibrationFormDialog:
        return CalibrationFormDialog(
            self.service.get_customer_options(),
            self.service.study_repository.get_all(),
            self.service.country_repository.get_all(),
            self.service.site_repository.get_all(),
            self.service.quote_repository.get_all(),
            self.service.get_supplier_options(),
            self.service.get_status_options(),
            self,
        )

    def _handle_row_click(self, index: QModelIndex) -> None:
        self._update_selected_calibration(index.row())

    def _handle_row_double_click(self, index: Any) -> None:
        self._update_selected_calibration(index.row())
        self.edit_calibration()

    def _on_selection_changed(self, selected: Any, deselected: Any) -> None:
        if not selected.indexes():
            self._selected_calibration_id = None
            self.calibration_selected.emit(None)
            return

        self._update_selected_calibration(selected.indexes()[0].row())

    def _apply_search(self, query: str) -> None:
        selected_calibration_id = self._selected_calibration_id
        self.table_model.set_filter(query)
        self._restore_selection(selected_calibration_id)

    def _update_selected_calibration(self, row: int) -> None:
        self._selected_calibration_id = self.table_model.calibration_id_at(row)
        self.calibration_selected.emit(self._selected_calibration_id)

    def _restore_selection(self, calibration_id: str | None) -> None:
        self.table_view.clearSelection()
        if calibration_id is None:
            self._selected_calibration_id = None
            self.calibration_selected.emit(None)
            return

        for row in range(self.table_model.rowCount()):
            if self.table_model.calibration_id_at(row) == calibration_id:
                self.table_view.selectRow(row)
                self._selected_calibration_id = calibration_id
                self.calibration_selected.emit(calibration_id)
                return

        self._selected_calibration_id = None
        self.calibration_selected.emit(None)
