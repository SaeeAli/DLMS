from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenuBar,
    QPushButton,
    QStackedWidget,
    QStatusBar,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from ui.navigation_manager import NavigationManager
from ui.pages.dashboard_page import DashboardPage


class MainWindow(QMainWindow):
    """Professional main application window."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("DLMS")
        self.resize(1200, 760)
        self.setMinimumSize(900, 600)

        self._create_menu_bar()
        self._create_tool_bar()
        self._create_status_bar()
        self._create_central_layout()

        self.navigation_manager = NavigationManager(self._stacked_pages)
        self.navigation_manager.register(DashboardPage())
        self.navigation_manager.navigate("dashboard")

    def _create_menu_bar(self) -> None:
        menu_bar = self.menuBar()
        menu_bar.setNativeMenuBar(False)

        file_menu = menu_bar.addMenu("File")
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        view_menu = menu_bar.addMenu("View")
        dashboard_action = QAction("Dashboard", self)
        dashboard_action.triggered.connect(lambda: self.navigation_manager.navigate("dashboard"))
        view_menu.addAction(dashboard_action)

    def _create_tool_bar(self) -> None:
        toolbar = QToolBar("Main Toolbar", self)
        toolbar.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)

        dashboard_button = QPushButton("Dashboard", self)
        dashboard_button.clicked.connect(lambda: self.navigation_manager.navigate("dashboard"))
        toolbar.addWidget(dashboard_button)

    def _create_status_bar(self) -> None:
        status_bar = QStatusBar(self)
        self.setStatusBar(status_bar)
        status_bar.showMessage("Ready")

    def _create_central_layout(self) -> None:
        container = QWidget(self)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        nav_panel = QWidget(self)
        nav_panel.setFixedWidth(220)
        nav_panel.setObjectName("navPanel")
        nav_panel.setStyleSheet(
            "#navPanel { background: #f5f7fb; border: 1px solid #e0e4eb; border-left: 0; }"
        )
        nav_layout = QVBoxLayout(nav_panel)
        nav_layout.setContentsMargins(16, 16, 16, 16)
        nav_layout.setSpacing(8)

        nav_title = QLabel("Navigation")
        nav_title.setStyleSheet("font-size: 13px; font-weight: 600; color: #44506b;")
        nav_layout.addWidget(nav_title)

        placeholder = QLabel("Left navigation panel placeholder")
        placeholder.setWordWrap(True)
        placeholder.setStyleSheet("color: #6b7280; font-size: 12px;")
        nav_layout.addWidget(placeholder)
        nav_layout.addStretch(1)

        self._stacked_pages = QStackedWidget(self)
        self._stacked_pages.setObjectName("stackedPages")

        layout.addWidget(nav_panel)
        layout.addWidget(self._stacked_pages)

        self.setCentralWidget(container)
