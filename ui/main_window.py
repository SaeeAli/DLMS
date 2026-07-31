from __future__ import annotations

from PySide6.QtWidgets import QLabel, QMainWindow, QVBoxLayout, QWidget


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("DLMS")
        self.resize(900, 600)

        container = QWidget(self)
        layout = QVBoxLayout(container)

        label = QLabel("DLMS is ready for development.")
        label.setStyleSheet("font-size: 16px;")
        layout.addWidget(label)

        self.setCentralWidget(container)
