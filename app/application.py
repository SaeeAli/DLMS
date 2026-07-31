from __future__ import annotations

from PySide6.QtWidgets import QMainWindow

from ui.main_window import MainWindow


class Application:
    """Top-level application orchestrator."""

    def __init__(self) -> None:
        self.window: QMainWindow | None = None

    def run(self) -> None:
        self.window = MainWindow()
        self.window.show()
