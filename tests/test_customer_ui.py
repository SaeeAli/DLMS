import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QMessageBox
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from database.base import Base
from repositories.customer_repository import CustomerRepository
from services.customer_service import CustomerService
from ui.pages.customer_list_page import CustomerListPage


def test_customer_list_page_loads_and_filters_customers() -> None:
    app = QApplication.instance() or QApplication([])
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        service = CustomerService(CustomerRepository(session))
        page = CustomerListPage(service)

        service.create_customer(name="Acme", customer_code="ACM-001", contact_email="ops@example.com")
        page.refresh_customers()

        assert page.table_model.rowCount() == 1
        page.search_input.setText("acme")
        assert page.table_model.rowCount() == 1
        page.search_input.setText("missing")
        assert page.table_model.rowCount() == 0


def test_customer_page_selects_and_deletes_the_selected_customer(monkeypatch) -> None:
    app = QApplication.instance() or QApplication([])
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        service = CustomerService(CustomerRepository(session))
        page = CustomerListPage(service)

        first = service.create_customer(name="Alpha", customer_code="ALP-001")
        second = service.create_customer(name="Beta", customer_code="BET-001")
        page.refresh_customers()

        page.table_view.selectRow(1)
        assert page._selected_customer_id == second.id

        monkeypatch.setattr(
            "ui.pages.customer_list_page.QMessageBox.question",
            lambda *args, **kwargs: QMessageBox.StandardButton.Yes,
        )
        page.delete_selected_customer()

        remaining = service.get_all()
        assert len(remaining) == 1
        assert remaining[0].id == first.id
