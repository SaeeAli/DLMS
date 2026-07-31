from __future__ import annotations

from PySide6.QtWidgets import QWidget


class BasePage(QWidget):
    """Reusable base for all application pages."""

    page_name: str = ""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName(self.page_name or self.__class__.__name__)
