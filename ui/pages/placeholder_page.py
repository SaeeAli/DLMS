from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from ui.pages.base_page import BasePage


class PlaceholderPage(BasePage):
    """Reusable placeholder page for future module development."""

    def __init__(self, page_name: str, title: str, parent: QWidget | None = None) -> None:
        self.page_name = page_name
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 22px; font-weight: 600;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        placeholder = QLabel("Coming Soon")
        placeholder.setStyleSheet("font-size: 14px; color: #6b7280;")

        layout.addWidget(title_label)
        layout.addWidget(QLabel(""))
        layout.addWidget(placeholder)
        layout.addStretch(1)
