from __future__ import annotations

from datetime import datetime, timezone

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
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
        self.available_site_list = QListWidget(self)
        self.available_site_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.available_site_list.setMinimumHeight(120)
        self.available_site_list.setMaximumHeight(140)

        self.site_list = QListWidget(self)
        self.site_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.site_list.setMinimumHeight(120)
        self.site_list.setMaximumHeight(140)

        self.add_site_button = QPushButton("Add >", self)
        self.remove_site_button = QPushButton("< Remove", self)
        self.add_site_button.clicked.connect(self._add_selected_sites)
        self.remove_site_button.clicked.connect(self._remove_selected_sites)

        sites_selector = QWidget(self)
        sites_selector_layout = QHBoxLayout(sites_selector)
        sites_selector_layout.setContentsMargins(0, 0, 0, 0)
        sites_selector_layout.setSpacing(8)

        available_container = QWidget(self)
        available_layout = QVBoxLayout(available_container)
        available_layout.setContentsMargins(0, 0, 0, 0)
        available_layout.setSpacing(4)
        available_layout.addWidget(QLabel("Available Sites", self))
        available_layout.addWidget(self.available_site_list)

        action_container = QWidget(self)
        action_layout = QVBoxLayout(action_container)
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setSpacing(6)
        action_layout.addStretch(1)
        action_layout.addWidget(self.add_site_button)
        action_layout.addWidget(self.remove_site_button)
        action_layout.addStretch(1)

        selected_container = QWidget(self)
        selected_layout = QVBoxLayout(selected_container)
        selected_layout.setContentsMargins(0, 0, 0, 0)
        selected_layout.setSpacing(4)
        selected_layout.addWidget(QLabel("Selected Sites", self))
        selected_layout.addWidget(self.site_list)

        sites_selector_layout.addWidget(available_container, 1)
        sites_selector_layout.addWidget(action_container)
        sites_selector_layout.addWidget(selected_container, 1)

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
        form_layout.addRow("Sites", sites_selector)
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

        first_quote_site = quote.quote_sites[0] if quote.quote_sites else None
        site = first_quote_site.site if first_quote_site is not None else None
        assignment = site.study_country if site is not None else None
        study = assignment.study if assignment is not None else None
        country = assignment.country if assignment is not None else None

        customer_id = study.customer_id if study is not None else None
        study_id = study.id if study is not None else None
        country_id = country.id if country is not None else None
        selected_site_ids = {
            quote_site.site_id
            for quote_site in quote.quote_sites
            if quote_site.site_id is not None
        }

        customer_index = self.customer_combo.findData(customer_id)
        if customer_index >= 0:
            self.customer_combo.setCurrentIndex(customer_index)

        study_index = self.study_combo.findData(study_id)
        if study_index >= 0:
            self.study_combo.setCurrentIndex(study_index)

        country_index = self.country_combo.findData(country_id)
        if country_index >= 0:
            self.country_combo.setCurrentIndex(country_index)

        self._select_sites(selected_site_ids)

    def selected_customer_id(self) -> str | None:
        value = self.customer_combo.currentData()
        return value if value else None

    def selected_study_id(self) -> str | None:
        value = self.study_combo.currentData()
        return value if value else None

    def selected_country_id(self) -> str | None:
        value = self.country_combo.currentData()
        return value if value else None

    def selected_site_ids(self) -> list[str]:
        selected_ids: list[str] = []
        for i in range(self.site_list.count()):
            item = self.site_list.item(i)
            if item is None:
                continue
            site_id = item.data(Qt.ItemDataRole.UserRole)
            if site_id:
                selected_ids.append(site_id)
        return selected_ids

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
        selected_site_ids = set(self.selected_site_ids())
        self.available_site_list.clear()
        self.site_list.clear()
        if not study_id or not country_id:
            return

        available_items: list[tuple[str, str | None]] = []
        selected_items: list[tuple[str, str | None]] = []
        for site in self._all_sites:
            assignment = site.study_country
            if assignment is None:
                continue
            if study_id and assignment.study_id != study_id:
                continue
            if country_id and assignment.country_id != country_id:
                continue
            if site.id in selected_site_ids:
                selected_items.append((site.site_number or "", site.id))
            else:
                available_items.append((site.site_number or "", site.id))

        for site_number, site_id in available_items:
            item = QListWidgetItem(site_number)
            item.setData(Qt.ItemDataRole.UserRole, site_id)
            self.available_site_list.addItem(item)

        for site_number, site_id in selected_items:
            item = QListWidgetItem(site_number)
            item.setData(Qt.ItemDataRole.UserRole, site_id)
            self.site_list.addItem(item)

    def _select_sites(self, site_ids: set[str]) -> None:
        if not site_ids:
            return

        for i in range(self.available_site_list.count() - 1, -1, -1):
            item = self.available_site_list.item(i)
            if item is None:
                continue
            if item.data(Qt.ItemDataRole.UserRole) in site_ids:
                moved = self.available_site_list.takeItem(i)
                if moved is not None:
                    self.site_list.addItem(moved)

    def _add_selected_sites(self) -> None:
        selected = self.available_site_list.selectedItems()
        indices = sorted((self.available_site_list.row(item) for item in selected), reverse=True)
        for index in indices:
            moved = self.available_site_list.takeItem(index)
            if moved is not None:
                self.site_list.addItem(moved)

    def _remove_selected_sites(self) -> None:
        selected = self.site_list.selectedItems()
        indices = sorted((self.site_list.row(item) for item in selected), reverse=True)
        for index in indices:
            moved = self.site_list.takeItem(index)
            if moved is not None:
                self.available_site_list.addItem(moved)
