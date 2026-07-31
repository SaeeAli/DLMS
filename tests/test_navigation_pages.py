import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow


def test_main_window_registers_all_placeholder_pages() -> None:
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    window.show()

    expected_pages = {
        "dashboard",
        "devices",
        "customers",
        "suppliers",
        "sites",
        "calibrations",
        "certificates",
        "reports",
        "settings",
    }

    assert set(window.navigation_manager._pages.keys()) == expected_pages
    window.navigation_manager.navigate("customers")
    assert window.navigation_manager.current_page_name == "customers"
    app.quit()
