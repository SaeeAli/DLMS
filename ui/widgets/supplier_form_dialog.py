from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from models.supplier import Supplier


class SupplierFormDialog(QDialog):
    """Dialog for creating or editing a supplier."""

    YES_NO_VALUES: tuple[str, str] = ("No", "Yes")

    def __init__(self, currency_options: list[str], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Supplier")
        self.resize(560, 480)

        self.name_input = QLineEdit(self)
        self.country_input = QLineEdit(self)
        self.city_input = QLineEdit(self)
        self.address_input = QLineEdit(self)
        self.contact_person_input = QLineEdit(self)
        self.email_input = QLineEdit(self)
        self.phone_input = QLineEdit(self)

        self.on_site_calibration_combo = QComboBox(self)
        self.on_site_calibration_combo.addItems(self.YES_NO_VALUES)

        self.exchange_device_available_combo = QComboBox(self)
        self.exchange_device_available_combo.addItems(self.YES_NO_VALUES)

        self.shipping_supported_combo = QComboBox(self)
        self.shipping_supported_combo.addItems(self.YES_NO_VALUES)

        self.currency_combo = QComboBox(self)
        self.currency_combo.setEditable(False)
        self.currency_combo.addItems(currency_options)

        self.default_calibration_lead_time_days_input = QSpinBox(self)
        self.default_calibration_lead_time_days_input.setMinimum(1)
        self.default_calibration_lead_time_days_input.setMaximum(3650)
        self.default_calibration_lead_time_days_input.setValue(1)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        form_layout.addRow("Supplier Name", self.name_input)
        form_layout.addRow("Country", self.country_input)
        form_layout.addRow("City", self.city_input)
        form_layout.addRow("Address", self.address_input)
        form_layout.addRow("Contact Person", self.contact_person_input)
        form_layout.addRow("Email", self.email_input)
        form_layout.addRow("Phone", self.phone_input)
        form_layout.addRow("On-site Calibration", self.on_site_calibration_combo)
        form_layout.addRow("Exchange Device Available", self.exchange_device_available_combo)
        form_layout.addRow("Shipping Supported", self.shipping_supported_combo)
        form_layout.addRow("Currency", self.currency_combo)
        form_layout.addRow("Default Calibration Lead Time (Days)", self.default_calibration_lead_time_days_input)
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

    def set_supplier(self, supplier: Supplier) -> None:
        self.name_input.setText(supplier.name or "")
        self.country_input.setText(supplier.country or "")
        self.city_input.setText(supplier.city or "")
        self.address_input.setText(supplier.address or "")
        self.contact_person_input.setText(supplier.contact_person or "")
        self.email_input.setText(supplier.email or "")
        self.phone_input.setText(supplier.phone or "")
        self.on_site_calibration_combo.setCurrentText("Yes" if supplier.on_site_calibration else "No")
        self.exchange_device_available_combo.setCurrentText("Yes" if supplier.exchange_device_available else "No")
        self.shipping_supported_combo.setCurrentText("Yes" if supplier.shipping_supported else "No")

        currency_index = self.currency_combo.findText(supplier.currency or "")
        if currency_index >= 0:
            self.currency_combo.setCurrentIndex(currency_index)
        elif self.currency_combo.count() > 0:
            self.currency_combo.setCurrentIndex(0)

        self.default_calibration_lead_time_days_input.setValue(max(1, supplier.default_calibration_lead_time_days or 1))

    def on_site_calibration_value(self) -> bool:
        return self.on_site_calibration_combo.currentText() == "Yes"

    def exchange_device_available_value(self) -> bool:
        return self.exchange_device_available_combo.currentText() == "Yes"

    def shipping_supported_value(self) -> bool:
        return self.shipping_supported_combo.currentText() == "Yes"
