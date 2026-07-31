from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from ui.pages.base_page import BasePage


class DashboardPage(BasePage):
    """Initial dashboard page for the application."""

    page_name = "dashboard"

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel("Dashboard")
        title.setStyleSheet("font-size: 22px; font-weight: 600;")
        title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        subtitle = QLabel("Welcome to the DLMS desktop application.")
        subtitle.setStyleSheet("font-size: 12px; color: #666;")

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch(1)
