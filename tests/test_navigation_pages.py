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
        "studies",
        "countries",
        "quotes",
        "suppliers",
        "calibrations",
        "certificates",
        "reports",
        "settings",
    }

    assert set(window.navigation_manager._pages.keys()) == expected_pages
    window.navigation_manager.navigate("customers")
    assert window.navigation_manager.current_page_name == "customers"
    app.quit()


def test_navigation_highlights_only_one_button_at_a_time() -> None:
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    window.show()

    for page_name in ["dashboard", "devices", "customers", "studies", "countries", "quotes", "suppliers", "calibrations", "certificates", "reports", "settings"]:
        window.navigation_manager.navigate(page_name)
        active_buttons = [button for button in window.navigation_buttons.values() if button.isChecked()]
        assert len(active_buttons) == 1, f"Expected one active navigation button for {page_name}, got {len(active_buttons)}"
        assert window.navigation_buttons[page_name].isChecked()

    app.quit()
