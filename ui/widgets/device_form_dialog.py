from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from models.device import Device


class DeviceFormDialog(QDialog):
    """Dialog for creating or editing a device."""

    DEFAULT_DEVICE_TYPES: tuple[str, ...] = (
        "Centrifuge",
        "ECG",
        "Freezer",
        "Refrigerator",
        "Incubator",
        "Infusion Pump",
        "Syringe Pump",
        "Temperature Logger",
        "Pipette",
        "Balance",
        "Blood Pressure Monitor",
        "Thermometer",
        "Defibrillator",
        "Other",
    )

    def __init__(self, parent: QWidget | None = None, device_type_options: list[str] | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Device")
        self.resize(460, 260)

        self.brand_input = QLineEdit(self)
        self.device_type_combo = QComboBox(self)
        self.device_type_combo.setEditable(False)
        self.device_type_combo.addItems(device_type_options or list(self.DEFAULT_DEVICE_TYPES))
        self.device_type_combo.setCurrentText("")

        self.serial_number_input = QLineEdit(self)
        self.model_input = QLineEdit(self)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        form_layout.addRow("Brand", self.brand_input)
        form_layout.addRow("Type of Device", self.device_type_combo)
        form_layout.addRow("Model", self.model_input)
        form_layout.addRow("Serial Number", self.serial_number_input)
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

    def set_device(self, device: Device) -> None:
        self.brand_input.setText(device.brand or device.asset_tag or "")
        current_type = (device.device_type or "").strip()
        if current_type and self.device_type_combo.findText(current_type) < 0:
            # Preserve legacy/custom values when editing older rows.
            self.device_type_combo.addItem(current_type)
        self.device_type_combo.setCurrentText(current_type)
        self.model_input.setText(device.model or "")
        self.serial_number_input.setText(device.serial_number or "")
