import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from database.base import Base
from models.customer import Customer
from repositories.customer_repository import CustomerRepository
from repositories.study_repository import StudyRepository
from services.study_service import StudyService
from ui.pages.study_list_page import StudyListPage


def test_study_list_page_loads_and_filters_studies() -> None:
    app = QApplication.instance() or QApplication([])
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        customer_repository = CustomerRepository(session)
        study_repository = StudyRepository(session)
        service = StudyService(study_repository, customer_repository)

        customer = Customer(name="Acme")
        customer_repository.create(customer)
        service.create_study(customer=customer, study_number="ST-100", status="Active")

        page = StudyListPage(service)
        page.refresh_studies()

        assert page.table_model.rowCount() == 1
        page.search_input.setText("st-100")
        assert page.table_model.rowCount() == 1
        page.search_input.setText("missing")
        assert page.table_model.rowCount() == 0
