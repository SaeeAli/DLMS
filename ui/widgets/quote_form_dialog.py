from __future__ import annotations

from datetime import datetime, timezone

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from models.country import Country
from models.customer import Customer
from models.quote import Quote
from models.site import Site
from models.study import Study


class QuoteFormDialog(QDialog):
    """Dialog for creating or editing a quote."""

    def __init__(self, customers: list[Customer], studies: list[Study], countries: list[Country], sites: list[Site], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Quote")
        self.resize(560, 420)

        self._all_studies = studies
        self._all_countries = countries
        self._all_sites = sites

        self.quote_number_input = QLineEdit(self)

        self.customer_combo = QComboBox(self)
        self.customer_combo.addItem("", "")
        for customer in customers:
            self.customer_combo.addItem(customer.name, customer.id)

        self.study_combo = QComboBox(self)
        self.country_combo = QComboBox(self)
        self.site_combo = QComboBox(self)

        self.quote_date_input = QDateEdit(self)
        self.quote_date_input.setCalendarPopup(True)
        self.quote_date_input.setDate(QDate.currentDate())

        self.status_combo = QComboBox(self)
        self.status_combo.addItems(["Draft", "Sent", "Approved", "Rejected", "Expired"])
        self.notes_input = QTextEdit(self)

        self.customer_combo.currentIndexChanged.connect(self._on_customer_changed)
        self.study_combo.currentIndexChanged.connect(self._on_study_changed)
        self.country_combo.currentIndexChanged.connect(self._on_country_changed)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        form_layout.addRow("Quote Number", self.quote_number_input)
        form_layout.addRow("Customer", self.customer_combo)
        form_layout.addRow("Study Number", self.study_combo)
        form_layout.addRow("Country", self.country_combo)
        form_layout.addRow("Site Number", self.site_combo)
        form_layout.addRow("Quote Date", self.quote_date_input)
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
        self._populate_countries(None)
        self._populate_sites(None, None)

    def set_quote(self, quote: Quote) -> None:
        self.quote_number_input.setText(quote.quote_number or "")
        self.status_combo.setCurrentText(quote.status or "Draft")
        self.notes_input.setPlainText(quote.notes or "")

        if quote.quote_date is not None:
            local_date = quote.quote_date.date()
            self.quote_date_input.setDate(QDate(local_date.year, local_date.month, local_date.day))

        site = quote.site
        assignment = site.study_country if site is not None else None
        study = assignment.study if assignment is not None else None
        country = assignment.country if assignment is not None else None

        customer_id = study.customer_id if study is not None else None
        study_id = study.id if study is not None else None
        country_id = country.id if country is not None else None
        site_id = site.id if site is not None else None

        customer_index = self.customer_combo.findData(customer_id)
        if customer_index >= 0:
            self.customer_combo.setCurrentIndex(customer_index)

        study_index = self.study_combo.findData(study_id)
        if study_index >= 0:
            self.study_combo.setCurrentIndex(study_index)

        country_index = self.country_combo.findData(country_id)
        if country_index >= 0:
            self.country_combo.setCurrentIndex(country_index)

        site_index = self.site_combo.findData(site_id)
        if site_index >= 0:
            self.site_combo.setCurrentIndex(site_index)

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

    def selected_quote_date(self) -> datetime:
        d = self.quote_date_input.date()
        return datetime(d.year(), d.month(), d.day(), tzinfo=timezone.utc)

    def _on_customer_changed(self) -> None:
        customer_id = self.selected_customer_id()
        self._populate_studies(customer_id)
        self._populate_countries(None)
        self._populate_sites(None, None)

    def _on_study_changed(self) -> None:
        study_id = self.selected_study_id()
        self._populate_countries(study_id)
        self._populate_sites(study_id, None)

    def _on_country_changed(self) -> None:
        self._populate_sites(self.selected_study_id(), self.selected_country_id())

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
            if study_id and study_id not in country_studies:
                continue
            self.country_combo.addItem(country.name or "", country.id)
        self.country_combo.blockSignals(False)

    def _populate_sites(self, study_id: str | None, country_id: str | None) -> None:
        self.site_combo.clear()
        self.site_combo.addItem("", "")
        if not study_id or not country_id:
            return
        for site in self._all_sites:
            assignment = site.study_country
            if assignment is None:
                continue
            if study_id and assignment.study_id != study_id:
                continue
            if country_id and assignment.country_id != country_id:
                continue
            self.site_combo.addItem(site.site_number or "", site.id)
