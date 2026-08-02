from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from models.customer import Customer
from models.study import Study


class StudyFormDialog(QDialog):
    """Dialog for creating or editing a study."""

    def __init__(self, customers: list[Customer], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Study")
        self.resize(480, 320)

        self.customer_combo = QComboBox(self)
        self.customer_combo.addItem("", "")
        for customer in customers:
            self.customer_combo.addItem(customer.name or customer.customer_code, customer.id)

        self.study_number_input = QLineEdit(self)
        self.study_name_input = QLineEdit(self)
        self.status_combo = QComboBox(self)
        self.status_combo.addItems(["Active", "Inactive", "Completed"])
        self.notes_input = QTextEdit(self)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        form_layout.addRow("Customer", self.customer_combo)
        form_layout.addRow("Study Number", self.study_number_input)
        form_layout.addRow("Study Name", self.study_name_input)
        form_layout.addRow("Status", self.status_combo)
        form_layout.addRow("Notes", self.notes_input)
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

    def set_study(self, study: Study) -> None:
        self.study_number_input.setText(study.study_number or "")
        self.study_name_input.setText(study.study_name or "")
        self.status_combo.setCurrentText(study.status or "Active")
        self.notes_input.setPlainText(study.notes or "")
        if study.customer_id is not None:
            index = self.customer_combo.findData(study.customer_id)
            if index >= 0:
                self.customer_combo.setCurrentIndex(index)

    def selected_customer_id(self) -> str | None:
        value = self.customer_combo.currentData()
        return value if value else None
