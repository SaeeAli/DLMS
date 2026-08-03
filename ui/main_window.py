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

from database.session import SessionLocal
from repositories.country_repository import CountryRepository
from repositories.customer_repository import CustomerRepository
from repositories.device_repository import DeviceRepository
from repositories.quote_repository import QuoteRepository
from repositories.site_repository import SiteRepository
from repositories.study_country_repository import StudyCountryRepository
from repositories.study_repository import StudyRepository
from repositories.supplier_repository import SupplierRepository
from services.country_service import CountryService
from services.customer_service import CustomerService
from services.device_service import DeviceService
from services.quote_service import QuoteService
from services.study_service import StudyService
from services.supplier_service import SupplierService
from ui.navigation_manager import NavigationManager
from ui.pages.country_list_page import CountryListPage
from ui.pages.customer_list_page import CustomerListPage
from ui.pages.dashboard_page import DashboardPage
from ui.pages.device_list_page import DeviceListPage
from ui.pages.placeholder_page import PlaceholderPage
from ui.pages.quote_list_page import QuoteListPage
from ui.pages.study_list_page import StudyListPage
from ui.pages.supplier_list_page import SupplierListPage


class MainWindow(QMainWindow):
    """Professional main application window."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("DLMS")
        self.resize(1200, 760)
        self.setMinimumSize(900, 600)

        self._navigation_page_names = []
        self._create_menu_bar()
        self._create_tool_bar()
        self._create_status_bar()
        self._create_central_layout()

        self.navigation_manager = NavigationManager(self._stacked_pages, self._update_navigation_button_state)
        self.navigation_manager.register(DashboardPage())

        session = SessionLocal()
        study_country_repository = StudyCountryRepository(session)
        device_service = DeviceService(DeviceRepository(session))
        customer_service = CustomerService(CustomerRepository(session))
        study_service = StudyService(StudyRepository(session), CustomerRepository(session))
        country_service = CountryService(study_country_repository, CountryRepository(session), StudyRepository(session), SiteRepository(session))
        quote_service = QuoteService(
            QuoteRepository(session),
            CustomerRepository(session),
            StudyRepository(session),
            StudyCountryRepository(session),
            SiteRepository(session),
            CountryRepository(session),
        )
        supplier_service = SupplierService(SupplierRepository(session))
        self.navigation_manager.register(DeviceListPage(device_service))
        self.navigation_manager.register(CustomerListPage(customer_service))
        self.navigation_manager.register(StudyListPage(study_service))
        self.navigation_manager.register(CountryListPage(country_service))
        self.navigation_manager.register(QuoteListPage(quote_service))
        self.navigation_manager.register(SupplierListPage(supplier_service))

        placeholder_pages = {
            "calibrations": PlaceholderPage("calibrations", "Calibration Management"),
            "certificates": PlaceholderPage("certificates", "Certificate Management"),
            "reports": PlaceholderPage("reports", "Reports"),
            "settings": PlaceholderPage("settings", "Settings"),
        }
        for page in placeholder_pages.values():
            self.navigation_manager.register(page)

        self.navigation_manager.navigate("dashboard")
        self._update_navigation_button_state("dashboard")

    def _create_menu_bar(self) -> None:
        menu_bar = self.menuBar()
        menu_bar.setNativeMenuBar(False)

        file_menu = menu_bar.addMenu("File")
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        view_menu = menu_bar.addMenu("View")
        dashboard_action = QAction("Dashboard", self)
        dashboard_action.triggered.connect(lambda: self._navigate_to_page("dashboard"))
        view_menu.addAction(dashboard_action)

        devices_action = QAction("Device Management", self)
        devices_action.triggered.connect(lambda: self._navigate_to_page("devices"))
        view_menu.addAction(devices_action)

    def _create_tool_bar(self) -> None:
        toolbar = QToolBar("Main Toolbar", self)
        toolbar.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)

        dashboard_button = QPushButton("Dashboard", self)
        dashboard_button.clicked.connect(lambda: self._navigate_to_page("dashboard"))
        toolbar.addWidget(dashboard_button)

        devices_button = QPushButton("Device Management", self)
        devices_button.clicked.connect(lambda: self._navigate_to_page("devices"))
        toolbar.addWidget(devices_button)

        studies_button = QPushButton("Study Management", self)
        studies_button.clicked.connect(lambda: self._navigate_to_page("studies"))
        toolbar.addWidget(studies_button)

        countries_button = QPushButton("Country Management", self)
        countries_button.clicked.connect(lambda: self._navigate_to_page("countries"))
        toolbar.addWidget(countries_button)

        quotes_button = QPushButton("Quote Management", self)
        quotes_button.clicked.connect(lambda: self._navigate_to_page("quotes"))
        toolbar.addWidget(quotes_button)

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

        self.navigation_buttons = {}
        for page_name, label in [
            ("dashboard", "Dashboard"),
            ("devices", "Device Management"),
            ("customers", "Customer Management"),
            ("studies", "Study Management"),
            ("countries", "Country Management"),
            ("quotes", "Quote Management"),
            ("suppliers", "Supplier Management"),
            ("calibrations", "Calibration Management"),
            ("certificates", "Certificate Management"),
            ("reports", "Reports"),
            ("settings", "Settings"),
        ]:
            button = QPushButton(label, self)
            button.setCheckable(True)
            button.setChecked(False)
            button.setStyleSheet(
                "QPushButton { text-align: left; padding: 8px 10px; border: 1px solid #d7dce5; border-radius: 6px; background-color: #f8f9fc; color: #374151; }"
                "QPushButton:hover { background-color: #eef2ff; }"
                "QPushButton:checked { background-color: #ef4444; color: white; border-color: #ef4444; }"
            )
            button.clicked.connect(lambda checked=False, name=page_name: self._navigate_to_page(name))
            nav_layout.addWidget(button)
            self.navigation_buttons[page_name] = button
            self._navigation_page_names.append(page_name)

        nav_layout.addStretch(1)

        self._stacked_pages = QStackedWidget(self)
        self._stacked_pages.setObjectName("stackedPages")

        layout.addWidget(nav_panel)
        layout.addWidget(self._stacked_pages)

        self.setCentralWidget(container)

    def _navigate_to_page(self, page_name: str) -> None:
        self.navigation_manager.navigate(page_name)
        self._update_navigation_button_state(page_name)

    def _update_navigation_button_state(self, active_page_name: str) -> None:
        for page_name, button in self.navigation_buttons.items():
            button.setChecked(page_name == active_page_name)
