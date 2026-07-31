from __future__ import annotations

from PySide6.QtWidgets import QStackedWidget, QWidget

from ui.pages.base_page import BasePage


class NavigationManager:
    """Manages stacked page navigation for the application."""

    def __init__(self, stacked_widget: QStackedWidget) -> None:
        self._stacked_widget = stacked_widget
        self._pages: dict[str, BasePage] = {}

    def register(self, page: BasePage) -> None:
        self._pages[page.page_name] = page
        self._stacked_widget.addWidget(page)

    def navigate(self, page_name: str) -> BasePage:
        if page_name not in self._pages:
            raise KeyError(f"Unknown page: {page_name}")

        self._stacked_widget.setCurrentWidget(self._pages[page_name])
        return self._pages[page_name]

    def current_page(self) -> BasePage | None:
        return self._stacked_widget.currentWidget()

    @property
    def current_page_name(self) -> str:
        current_page = self.current_page()
        return current_page.page_name if current_page is not None else ""
