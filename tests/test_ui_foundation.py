import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow
from ui.pages.dashboard_page import DashboardPage


def test_main_window_starts_on_dashboard_page() -> None:
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    window.show()

    assert window.navigation_manager.current_page_name == "dashboard"
    assert isinstance(window.navigation_manager.current_page(), DashboardPage)
    assert window.centralWidget() is not None

    app.quit()
