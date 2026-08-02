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
from models.site import Site


class CountryFormDialog(QDialog):
    """Dialog for creating or editing country management records."""

    def __init__(self, customers: list[Customer], studies: list[Study], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Country")
        self.resize(480, 320)

        self._all_studies = studies

        self.customer_combo = QComboBox(self)
        self.customer_combo.addItem("", "")
        for customer in customers:
            self.customer_combo.addItem(customer.name, customer.id)

        self.study_combo = QComboBox(self)
        self.study_combo.addItem("", "")
        self.customer_combo.currentIndexChanged.connect(self._on_customer_changed)

        self.country_input = QLineEdit(self)
        self.site_number_input = QLineEdit(self)
        self.status_combo = QComboBox(self)
        self.status_combo.addItems(["Active", "Inactive"])
        self.notes_input = QTextEdit(self)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        form_layout.addRow("Customer", self.customer_combo)
        form_layout.addRow("Study", self.study_combo)
        form_layout.addRow("Country", self.country_input)
        form_layout.addRow("Site Number", self.site_number_input)
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

        self._populate_studies(None)

    def set_country(self, site: Site) -> None:
        self.country_input.setText(site.study_country.country.name if site.study_country and site.study_country.country else "")
        self.site_number_input.setText(site.site_number or "")
        self.status_combo.setCurrentText(site.status or "Active")
        self.notes_input.setPlainText(site.notes or "")
        if site.study_country_id is not None:
            assignment = site.study_country
            study = assignment.study if assignment is not None else None
            customer_id = study.customer_id if study is not None else None
            study_id = assignment.study_id if assignment is not None else None
            customer_index = self.customer_combo.findData(customer_id)
            if customer_index >= 0:
                self.customer_combo.setCurrentIndex(customer_index)
            study_index = self.study_combo.findData(study_id)
            if study_index >= 0:
                self.study_combo.setCurrentIndex(study_index)

    def selected_customer_id(self) -> str | None:
        value = self.customer_combo.currentData()
        return value if value else None

    def selected_study_id(self) -> str | None:
        value = self.study_combo.currentData()
        return value if value else None

    def _on_customer_changed(self) -> None:
        self._populate_studies(self.selected_customer_id())

    def _populate_studies(self, customer_id: str | None) -> None:
        self.study_combo.blockSignals(True)
        self.study_combo.clear()
        self.study_combo.addItem("", "")
        for study in self._all_studies:
            if customer_id and study.customer_id != customer_id:
                continue
            self.study_combo.addItem(study.study_number or "", study.id)
        self.study_combo.blockSignals(False)
