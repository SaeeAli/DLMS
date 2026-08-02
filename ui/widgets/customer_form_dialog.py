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

from models.customer import Customer


class CustomerFormDialog(QDialog):
    """Dialog for creating or editing a customer."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Customer")
        self.resize(420, 220)

        self.name_input = QLineEdit(self)
        self.customer_code_input = QLineEdit(self)
        self.contact_email_input = QLineEdit(self)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        form_layout.addRow("Name", self.name_input)
        form_layout.addRow("Customer Code", self.customer_code_input)
        form_layout.addRow("Contact Email", self.contact_email_input)
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

    def set_customer(self, customer: Customer) -> None:
        self.name_input.setText(customer.name or "")
        self.customer_code_input.setText(customer.customer_code or "")
        self.contact_email_input.setText(customer.contact_email or "")
