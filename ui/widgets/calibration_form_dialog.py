from __future__ import annotations

from datetime import datetime, timezone

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from models.calibration import Calibration
from models.country import Country
from models.customer import Customer
from models.quote import Quote
from models.site import Site
from models.study import Study
from models.supplier import Supplier


class CalibrationFormDialog(QDialog):
    """Dialog for creating or editing a calibration record."""

    def __init__(
        self,
        customers: list[Customer],
        studies: list[Study],
        countries: list[Country],
        sites: list[Site],
        quotes: list[Quote],
        suppliers: list[Supplier],
        status_options: list[str],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Calibration")
        self.resize(640, 560)

        self._all_studies = studies
        self._all_countries = countries
        self._all_sites = sites
        self._all_quotes = quotes

        self.customer_combo = QComboBox(self)
        self.customer_combo.addItem("", "")
        for customer in customers:
            self.customer_combo.addItem(customer.name, customer.id)

        self.study_combo = QComboBox(self)
        self.country_combo = QComboBox(self)
        self.site_combo = QComboBox(self)
        self.quote_combo = QComboBox(self)
        self.device_combo = QComboBox(self)

        self.supplier_combo = QComboBox(self)
        self.supplier_combo.addItem("", "")
        for supplier in suppliers:
            self.supplier_combo.addItem(supplier.name, supplier.id)

        self.calibration_start_date_input = QDateEdit(self)
        self.calibration_start_date_input.setCalendarPopup(True)
        self.calibration_start_date_input.setDate(QDate.currentDate())

        self.calibration_cycle_months_input = QSpinBox(self)
        self.calibration_cycle_months_input.setMinimum(1)
        self.calibration_cycle_months_input.setMaximum(120)
        self.calibration_cycle_months_input.setValue(12)

        self.calibration_due_date_input = QDateEdit(self)
        self.calibration_due_date_input.setCalendarPopup(True)
        self.calibration_due_date_input.setDate(QDate.currentDate())

        self.outbound_tracking_number_input = QLineEdit(self)

        self.delivery_date_enabled = QCheckBox("Delivery Date Set", self)
        self.delivery_date_input = QDateEdit(self)
        self.delivery_date_input.setCalendarPopup(True)
        self.delivery_date_input.setDate(QDate.currentDate())
        self.delivery_date_input.setEnabled(False)
        self.delivery_date_enabled.toggled.connect(self.delivery_date_input.setEnabled)

        self.delivery_confirmed_input = QCheckBox("Delivery Confirmed", self)

        self.return_tracking_number_input = QLineEdit(self)

        self.return_received_date_enabled = QCheckBox("Return Received Date Set", self)
        self.return_received_date_input = QDateEdit(self)
        self.return_received_date_input.setCalendarPopup(True)
        self.return_received_date_input.setDate(QDate.currentDate())
        self.return_received_date_input.setEnabled(False)
        self.return_received_date_enabled.toggled.connect(self.return_received_date_input.setEnabled)

        self.status_combo = QComboBox(self)
        self.status_combo.addItems(status_options)

        self.customer_combo.currentIndexChanged.connect(self._on_customer_changed)
        self.study_combo.currentIndexChanged.connect(self._on_study_changed)
        self.country_combo.currentIndexChanged.connect(self._on_country_changed)
        self.site_combo.currentIndexChanged.connect(self._on_site_changed)
        self.quote_combo.currentIndexChanged.connect(self._on_quote_changed)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        form_layout.addRow("Customer", self.customer_combo)
        form_layout.addRow("Study", self.study_combo)
        form_layout.addRow("Country", self.country_combo)
        form_layout.addRow("Site", self.site_combo)
        form_layout.addRow("Quote", self.quote_combo)
        form_layout.addRow("Device", self.device_combo)
        form_layout.addRow("Supplier", self.supplier_combo)
        form_layout.addRow("Calibration Start Date", self.calibration_start_date_input)
        form_layout.addRow("Calibration Cycle (Months)", self.calibration_cycle_months_input)
        form_layout.addRow("Calibration Due Date", self.calibration_due_date_input)
        form_layout.addRow("Outbound Tracking Number", self.outbound_tracking_number_input)

        delivery_container = QWidget(self)
        delivery_layout = QHBoxLayout(delivery_container)
        delivery_layout.setContentsMargins(0, 0, 0, 0)
        delivery_layout.setSpacing(8)
        delivery_layout.addWidget(self.delivery_date_enabled)
        delivery_layout.addWidget(self.delivery_date_input, 1)
        form_layout.addRow("Delivery Date", delivery_container)

        form_layout.addRow("Delivery Confirmed", self.delivery_confirmed_input)
        form_layout.addRow("Return Tracking Number", self.return_tracking_number_input)

        return_container = QWidget(self)
        return_layout = QHBoxLayout(return_container)
        return_layout.setContentsMargins(0, 0, 0, 0)
        return_layout.setSpacing(8)
        return_layout.addWidget(self.return_received_date_enabled)
        return_layout.addWidget(self.return_received_date_input, 1)
        form_layout.addRow("Return Received Date", return_container)

        form_layout.addRow("Status", self.status_combo)
        layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        save_button = QPushButton("Save", self)
        save_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel", self)
        cancel_button.clicked.connect(self.reject)
        button_layout.addStretch(1)
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        self._populate_studies(None)
        self._populate_countries(None)
        self._populate_sites(None, None)
        self._populate_quotes(None)
        self._populate_devices(None)

    def set_calibration(self, calibration: Calibration) -> None:
        customer_index = self.customer_combo.findData(calibration.customer_id)
        if customer_index >= 0:
            self.customer_combo.setCurrentIndex(customer_index)

        study_index = self.study_combo.findData(calibration.study_id)
        if study_index >= 0:
            self.study_combo.setCurrentIndex(study_index)

        country_index = self.country_combo.findData(calibration.country_id)
        if country_index >= 0:
            self.country_combo.setCurrentIndex(country_index)

        site_index = self.site_combo.findData(calibration.site_id)
        if site_index >= 0:
            self.site_combo.setCurrentIndex(site_index)

        quote_index = self.quote_combo.findData(calibration.quote_id)
        if quote_index >= 0:
            self.quote_combo.setCurrentIndex(quote_index)

        device_index = self.device_combo.findData(calibration.device_id)
        if device_index >= 0:
            self.device_combo.setCurrentIndex(device_index)

        supplier_index = self.supplier_combo.findData(calibration.supplier_id)
        if supplier_index >= 0:
            self.supplier_combo.setCurrentIndex(supplier_index)

        self.calibration_start_date_input.setDate(self._to_qdate(calibration.calibration_start_date))
        self.calibration_cycle_months_input.setValue(calibration.calibration_cycle_months)
        self.calibration_due_date_input.setDate(self._to_qdate(calibration.calibration_due_date))

        self.outbound_tracking_number_input.setText(calibration.outbound_tracking_number or "")
        if calibration.delivery_date is not None:
            self.delivery_date_enabled.setChecked(True)
            self.delivery_date_input.setDate(self._to_qdate(calibration.delivery_date))
        else:
            self.delivery_date_enabled.setChecked(False)

        self.delivery_confirmed_input.setChecked(calibration.delivery_confirmed)
        self.return_tracking_number_input.setText(calibration.return_tracking_number or "")

        if calibration.return_received_date is not None:
            self.return_received_date_enabled.setChecked(True)
            self.return_received_date_input.setDate(self._to_qdate(calibration.return_received_date))
        else:
            self.return_received_date_enabled.setChecked(False)

        self.status_combo.setCurrentText(calibration.status)

    def selected_customer_id(self) -> str | None:
        value = self.customer_combo.currentData()
        return value if value else None

    def selected_study_id(self) -> str | None:
        value = self.study_combo.currentData()
        return value if value else None

    def selected_country_id(self) -> str | None:
        value = self.country_combo.currentData()
        return value if value else None

    def selected_site_id(self) -> str | None:
        value = self.site_combo.currentData()
        return value if value else None

    def selected_quote_id(self) -> str | None:
        value = self.quote_combo.currentData()
        return value if value else None

    def selected_device_id(self) -> str | None:
        value = self.device_combo.currentData()
        return value if value else None

    def selected_supplier_id(self) -> str | None:
        value = self.supplier_combo.currentData()
        return value if value else None

    def selected_calibration_start_date(self) -> datetime:
        return self._selected_datetime(self.calibration_start_date_input)

    def selected_calibration_due_date(self) -> datetime:
        return self._selected_datetime(self.calibration_due_date_input)

    def selected_delivery_date(self) -> datetime | None:
        if not self.delivery_date_enabled.isChecked():
            return None
        return self._selected_datetime(self.delivery_date_input)

    def selected_return_received_date(self) -> datetime | None:
        if not self.return_received_date_enabled.isChecked():
            return None
        return self._selected_datetime(self.return_received_date_input)

    def _selected_datetime(self, date_edit: QDateEdit) -> datetime:
        date_value = date_edit.date()
        return datetime(date_value.year(), date_value.month(), date_value.day(), tzinfo=timezone.utc)

    def _to_qdate(self, value: datetime) -> QDate:
        local_date = value.date()
        return QDate(local_date.year, local_date.month, local_date.day)

    def _on_customer_changed(self) -> None:
        customer_id = self.selected_customer_id()
        self._populate_studies(customer_id)
        self._populate_countries(None)
        self._populate_sites(None, None)
        self._populate_quotes(None)
        self._populate_devices(None)

    def _on_study_changed(self) -> None:
        study_id = self.selected_study_id()
        self._populate_countries(study_id)
        self._populate_sites(study_id, None)
        self._populate_quotes(None)
        self._populate_devices(None)

    def _on_country_changed(self) -> None:
        self._populate_sites(self.selected_study_id(), self.selected_country_id())
        self._populate_quotes(None)
        self._populate_devices(None)

    def _on_site_changed(self) -> None:
        self._populate_quotes(self.selected_site_id())
        self._populate_devices(None)

    def _on_quote_changed(self) -> None:
        self._populate_devices(self.selected_quote_id())

    def _populate_studies(self, customer_id: str | None) -> None:
        self.study_combo.blockSignals(True)
        self.study_combo.clear()
        self.study_combo.addItem("", "")
        for study in self._all_studies:
            if customer_id and study.customer_id != customer_id:
                continue
            self.study_combo.addItem(study.study_number or "", study.id)
        self.study_combo.blockSignals(False)

    def _populate_countries(self, study_id: str | None) -> None:
        self.country_combo.blockSignals(True)
        self.country_combo.clear()
        self.country_combo.addItem("", "")
        if not study_id:
            self.country_combo.blockSignals(False)
            return

        for country in self._all_countries:
            country_studies = {
                site.study_country.study_id
                for site in self._all_sites
                if site.study_country is not None and site.study_country.country_id == country.id
            }
            if study_id not in country_studies:
                continue
            self.country_combo.addItem(country.name or "", country.id)
        self.country_combo.blockSignals(False)

    def _populate_sites(self, study_id: str | None, country_id: str | None) -> None:
        self.site_combo.blockSignals(True)
        self.site_combo.clear()
        self.site_combo.addItem("", "")
        if not study_id or not country_id:
            self.site_combo.blockSignals(False)
            return

        for site in self._all_sites:
            assignment = site.study_country
            if assignment is None:
                continue
            if assignment.study_id != study_id:
                continue
            if assignment.country_id != country_id:
                continue
            self.site_combo.addItem(site.site_number or "", site.id)
        self.site_combo.blockSignals(False)

    def _populate_quotes(self, site_id: str | None) -> None:
        self.quote_combo.blockSignals(True)
        self.quote_combo.clear()
        self.quote_combo.addItem("", "")
        if not site_id:
            self.quote_combo.blockSignals(False)
            return

        for quote in self._all_quotes:
            if any(quote_site.site_id == site_id for quote_site in quote.quote_sites):
                self.quote_combo.addItem(quote.quote_number or "", quote.id)
        self.quote_combo.blockSignals(False)

    def _populate_devices(self, quote_id: str | None) -> None:
        self.device_combo.clear()
        self.device_combo.addItem("", "")
        if not quote_id:
            return

        quote = next((item for item in self._all_quotes if item.id == quote_id), None)
        if quote is None:
            return

        seen_ids: set[str] = set()
        for quote_item in quote.quote_items:
            device = quote_item.device
            if device is None or device.id is None or device.id in seen_ids:
                continue
            seen_ids.add(device.id)
            label = " | ".join(
                part for part in [device.brand or "", device.model or "", device.serial_number or ""] if part
            )
            self.device_combo.addItem(label or "Device", device.id)
