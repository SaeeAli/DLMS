from __future__ import annotations

from PySide6.QtWidgets import (
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

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Device")
        self.resize(420, 220)

        self.asset_tag_input = QLineEdit(self)
        self.serial_number_input = QLineEdit(self)
        self.model_input = QLineEdit(self)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        form_layout.addRow("Device Name", self.asset_tag_input)
        form_layout.addRow("Serial Number", self.serial_number_input)
        form_layout.addRow("Model", self.model_input)
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
        self.asset_tag_input.setText(device.asset_tag or "")
        self.serial_number_input.setText(device.serial_number or "")
        self.model_input.setText(device.model or "")
