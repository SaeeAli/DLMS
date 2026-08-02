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

from models.study import Study
from models.study_country import StudyCountry


class CountryFormDialog(QDialog):
    """Dialog for creating or editing a study-country assignment."""

    def __init__(self, studies: list[Study], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Country")
        self.resize(480, 320)

        self.study_combo = QComboBox(self)
        self.study_combo.addItem("", "")
        for study in studies:
            label = f"{study.study_number} - {study.customer.name if study.customer else ''}".strip()
            self.study_combo.addItem(label, study.id)

        self.name_input = QLineEdit(self)
        self.country_code_input = QLineEdit(self)
        self.status_combo = QComboBox(self)
        self.status_combo.addItems(["Active", "Inactive"])
        self.notes_input = QTextEdit(self)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        form_layout.addRow("Study", self.study_combo)
        form_layout.addRow("Country Name", self.name_input)
        form_layout.addRow("Country Code", self.country_code_input)
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

    def set_country(self, assignment: StudyCountry) -> None:
        self.name_input.setText(assignment.country.name if assignment.country is not None else "")
        self.country_code_input.setText(assignment.country.country_code if assignment.country is not None else "")
        self.status_combo.setCurrentText(assignment.status or "Active")
        self.notes_input.setPlainText(assignment.notes or "")
        if assignment.study_id is not None:
            index = self.study_combo.findData(assignment.study_id)
            if index >= 0:
                self.study_combo.setCurrentIndex(index)

    def selected_study_id(self) -> str | None:
        value = self.study_combo.currentData()
        return value if value else None
