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

from models.site import Site
from models.study_country import StudyCountry


class SiteFormDialog(QDialog):
    """Dialog for creating or editing a site."""

    def __init__(self, study_countries: list[StudyCountry], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Site")
        self.resize(560, 380)

        self.study_country_combo = QComboBox(self)
        self.study_country_combo.addItem("", "")
        for assignment in study_countries:
            customer_name = assignment.study.customer.name if assignment.study and assignment.study.customer else ""
            study_number = assignment.study.study_number if assignment.study else ""
            country_name = assignment.country.name if assignment.country else ""
            label = f"{customer_name} | {study_number} | {country_name}"
            self.study_country_combo.addItem(label, assignment.id)

        self.site_number_input = QLineEdit(self)
        self.name_input = QLineEdit(self)
        self.address_input = QLineEdit(self)
        self.city_input = QLineEdit(self)
        self.status_combo = QComboBox(self)
        self.status_combo.addItems(["Active", "Inactive"])
        self.notes_input = QTextEdit(self)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        form_layout.addRow("Study / Country", self.study_country_combo)
        form_layout.addRow("Site Number", self.site_number_input)
        form_layout.addRow("Site Name", self.name_input)
        form_layout.addRow("Address", self.address_input)
        form_layout.addRow("City", self.city_input)
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

    def set_site(self, site: Site) -> None:
        self.site_number_input.setText(site.site_number or "")
        self.name_input.setText(site.name or "")
        self.address_input.setText(site.address or "")
        self.city_input.setText(site.city or "")
        self.status_combo.setCurrentText(site.status or "Active")
        self.notes_input.setPlainText(site.notes or "")
        if site.study_country_id is not None:
            index = self.study_country_combo.findData(site.study_country_id)
            if index >= 0:
                self.study_country_combo.setCurrentIndex(index)

    def selected_study_country_id(self) -> str | None:
        value = self.study_country_combo.currentData()
        return value if value else None
