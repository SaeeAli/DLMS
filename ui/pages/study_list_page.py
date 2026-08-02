from __future__ import annotations

from typing import Any

from PySide6.QtCore import QModelIndex, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QTableView,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from services.study_service import StudyService
from ui.pages.base_page import BasePage
from ui.widgets.study_form_dialog import StudyFormDialog
from ui.widgets.study_table_model import StudyTableModel


class StudyListPage(BasePage):
    """Page for managing studies through the service layer."""

    page_name = "studies"
    study_selected = Signal(object)

    def __init__(self, service: StudyService, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.service = service
        self._selected_study_id: str | None = None
        self._build_ui()
        self.refresh_studies()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        header = QLabel("Study Management")
        header.setStyleSheet("font-size: 22px; font-weight: 600;")
        layout.addWidget(header)

        toolbar = QToolBar("Study Toolbar")
        toolbar.setMovable(False)
        layout.addWidget(toolbar)

        add_action = QAction("Add Study", self)
        add_action.triggered.connect(self.add_study)
        toolbar.addAction(add_action)

        edit_action = QAction("Edit Study", self)
        edit_action.triggered.connect(self.edit_study)
        toolbar.addAction(edit_action)

        delete_action = QAction("Delete Study", self)
        delete_action.triggered.connect(self.delete_selected_study)
        toolbar.addAction(delete_action)

        refresh_action = QAction("Refresh", self)
        refresh_action.triggered.connect(self.refresh_studies)
        toolbar.addAction(refresh_action)

        search_container = QWidget(self)
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(8)

        search_label = QLabel("Search:")
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Customer, Study Number, Study Name, Status")
        self.search_input.textChanged.connect(self._apply_search)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input, 1)
        layout.addWidget(search_container)

        self.table_view = QTableView(self)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_view.setStyleSheet(
            "QTableView { background-color: white; gridline-color: #e5e7eb; }"
            "QTableView::item { padding: 6px; }"
            "QTableView::item:selected { background-color: #dfe9ff; color: #1f2a44; }"
        )
        self.table_view.clicked.connect(self._handle_row_click)
        self.table_view.doubleClicked.connect(self._handle_row_double_click)
        layout.addWidget(self.table_view, 1)

        self.table_model = StudyTableModel([])
        self.table_view.setModel(self.table_model)
        selection_model = self.table_view.selectionModel()
        if selection_model is not None:
            selection_model.selectionChanged.connect(self._on_selection_changed)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def refresh_studies(self) -> None:
        selected_study_id = self._selected_study_id
        studies = self.service.get_all()
        self.table_model.set_studies(studies)
        self._restore_selection(selected_study_id)

    def add_study(self) -> None:
        dialog = StudyFormDialog(self.service.get_customer_options(), self)
        if dialog.exec() == StudyFormDialog.Accepted:
            try:
                self.service.create_study(
                    customer=self.service.customer_repository.get_by_id(dialog.selected_customer_id() or ""),
                    study_number=dialog.study_number_input.text().strip(),
                    study_name=dialog.study_name_input.text().strip() or None,
                    status=dialog.status_combo.currentText(),
                    notes=dialog.notes_input.toPlainText().strip() or None,
                )
                self.refresh_studies()
            except ValueError as error:
                QMessageBox.warning(self, "Validation Error", str(error))

    def edit_study(self) -> None:
        if self._selected_study_id is None:
            QMessageBox.information(self, "Selection Required", "Select a study to edit.")
            return

        study = self.service.get_by_id(self._selected_study_id)
        if study is None:
            QMessageBox.warning(self, "Not Found", "The selected study could not be found.")
            return

        dialog = StudyFormDialog(self.service.get_customer_options(), self)
        dialog.set_study(study)
        if dialog.exec() == StudyFormDialog.Accepted:
            try:
                customer = self.service.customer_repository.get_by_id(dialog.selected_customer_id() or "")
                if customer is None:
                    raise ValueError("customer is required")
                self.service.update_study(
                    study,
                    customer=customer,
                    study_number=dialog.study_number_input.text().strip(),
                    study_name=dialog.study_name_input.text().strip() or None,
                    status=dialog.status_combo.currentText(),
                    notes=dialog.notes_input.toPlainText().strip() or None,
                )
                self.refresh_studies()
            except ValueError as error:
                QMessageBox.warning(self, "Validation Error", str(error))

    def delete_selected_study(self) -> None:
        if self._selected_study_id is None:
            QMessageBox.information(self, "Selection Required", "Select a study to delete.")
            return

        study = self.service.get_by_id(self._selected_study_id)
        if study is None:
            QMessageBox.warning(self, "Not Found", "The selected study could not be found.")
            return

        confirmation = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete study {study.study_number}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirmation == QMessageBox.StandardButton.Yes:
            try:
                self.service.delete_study(study)
                self.refresh_studies()
            except ValueError as error:
                QMessageBox.warning(self, "Delete Not Allowed", str(error))

    def _handle_row_click(self, index: QModelIndex) -> None:
        self._update_selected_study(index.row())

    def _handle_row_double_click(self, index: Any) -> None:
        self._update_selected_study(index.row())
        self.edit_study()

    def _on_selection_changed(self, selected: Any, deselected: Any) -> None:
        if not selected.indexes():
            self._selected_study_id = None
            self.study_selected.emit(None)
            return

        self._update_selected_study(selected.indexes()[0].row())

    def _apply_search(self, query: str) -> None:
        selected_study_id = self._selected_study_id
        self.table_model.set_filter(query)
        self._restore_selection(selected_study_id)

    def _update_selected_study(self, row: int) -> None:
        self._selected_study_id = self.table_model.study_id_at(row)
        self.study_selected.emit(self._selected_study_id)

    def _restore_selection(self, study_id: str | None) -> None:
        self.table_view.clearSelection()
        if study_id is None:
            self._selected_study_id = None
            self.study_selected.emit(None)
            return

        for row in range(self.table_model.rowCount()):
            if self.table_model.study_id_at(row) == study_id:
                self.table_view.selectRow(row)
                self._selected_study_id = study_id
                self.study_selected.emit(study_id)
                return

        self._selected_study_id = None
        self.study_selected.emit(None)
