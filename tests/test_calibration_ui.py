import os
from datetime import datetime, timezone

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from database.base import Base
from models.calibration import CalibrationStatus
from models.country import Country
from models.customer import Customer
from models.device import Device
from models.quote import Quote
from models.quote_item import QuoteItem
from models.quote_site import QuoteSite
from models.site import Site
from models.study import Study
from models.study_country import StudyCountry
from models.supplier import Supplier
from repositories.calibration_repository import CalibrationRepository
from repositories.country_repository import CountryRepository
from repositories.customer_repository import CustomerRepository
from repositories.device_repository import DeviceRepository
from repositories.quote_repository import QuoteRepository
from repositories.site_repository import SiteRepository
from repositories.study_country_repository import StudyCountryRepository
from repositories.study_repository import StudyRepository
from repositories.supplier_repository import SupplierRepository
from services.calibration_service import CalibrationService
from ui.pages.calibration_list_page import CalibrationListPage
from ui.widgets.calibration_form_dialog import CalibrationFormDialog


def _make_service(session: Session) -> CalibrationService:
    return CalibrationService(
        CalibrationRepository(session),
        CustomerRepository(session),
        StudyRepository(session),
        StudyCountryRepository(session),
        CountryRepository(session),
        SiteRepository(session),
        QuoteRepository(session),
        DeviceRepository(session),
        SupplierRepository(session),
    )


def _seed_entities(session: Session):
    customer = Customer(name="Acme")
    customer_two = Customer(name="Beta")
    study = Study(study_number="ST-100", customer=customer)
    study_two = Study(study_number="ST-200", customer=customer_two)
    country = Country(name="Germany")
    country_two = Country(name="France")
    assignment = StudyCountry(study=study, country=country)
    assignment_two = StudyCountry(study=study_two, country=country_two)
    site = Site(name="Berlin Site", site_number="S-001", study_country=assignment)
    site_two = Site(name="Paris Site", site_number="S-002", study_country=assignment_two)

    device = Device(brand="Fluke", device_type="Thermometer", model="T300", serial_number="SN-100", asset_number="Fluke")
    device_two = Device(brand="Keysight", device_type="Balance", model="B2", serial_number="SN-200", asset_number="Keysight")

    supplier = Supplier(
        name="MedTech GmbH",
        country="Germany",
        city="Berlin",
        address="Street 1",
        contact_person="Anna",
        email="anna@medtech.com",
        phone="+49-123",
        on_site_calibration=True,
        exchange_device_available=True,
        shipping_supported=True,
        currency="EUR (€)",
        default_calibration_lead_time_days=7,
    )

    quote = Quote(quote_number="Q-001", quote_date=datetime(2026, 1, 1, tzinfo=timezone.utc), status="Draft")
    quote.quote_sites = [QuoteSite(site=site)]
    quote_item = QuoteItem(quote=quote, device=device, quantity=1, unit_cost=10, unit_price=12)

    quote_two = Quote(quote_number="Q-002", quote_date=datetime(2026, 1, 1, tzinfo=timezone.utc), status="Draft")
    quote_two.quote_sites = [QuoteSite(site=site_two)]
    quote_item_two = QuoteItem(quote=quote_two, device=device_two, quantity=1, unit_cost=10, unit_price=12)

    session.add_all(
        [
            customer,
            customer_two,
            study,
            study_two,
            country,
            country_two,
            assignment,
            assignment_two,
            site,
            site_two,
            device,
            device_two,
            supplier,
            quote,
            quote_item,
            quote_two,
            quote_item_two,
        ]
    )
    session.flush()
    return customer, study, country, site, quote, device, supplier, customer_two, study_two


def test_calibration_list_page_loads_and_filters() -> None:
    app = QApplication.instance() or QApplication([])
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        service = _make_service(session)
        customer, study, country, site, quote, device, supplier, *_ = _seed_entities(session)

        service.create_calibration(
            customer_id=customer.id,
            study_id=study.id,
            country_id=country.id,
            site_id=site.id,
            quote_id=quote.id,
            device_id=device.id,
            supplier_id=supplier.id,
            calibration_start_date=datetime(2026, 2, 1, tzinfo=timezone.utc),
            calibration_cycle_months=12,
            calibration_due_date=datetime(2027, 2, 1, tzinfo=timezone.utc),
            status=CalibrationStatus.PENDING.value,
        )

        page = CalibrationListPage(service)
        page.refresh_calibrations()

        assert page.table_model.rowCount() == 1
        page.search_input.setText("acme")
        assert page.table_model.rowCount() == 1
        page.search_input.setText("sn-100")
        assert page.table_model.rowCount() == 1
        page.search_input.setText("missing")
        assert page.table_model.rowCount() == 0

    app.quit()


def test_calibration_form_dialog_applies_cascading_filters() -> None:
    app = QApplication.instance() or QApplication([])
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        service = _make_service(session)
        customer, study, country, site, quote, device, supplier, customer_two, study_two = _seed_entities(session)

        dialog = CalibrationFormDialog(
            [customer, customer_two],
            [study, study_two],
            [country],
            [site],
            [quote],
            [supplier],
            service.get_status_options(),
        )

        customer_index = dialog.customer_combo.findData(customer.id)
        dialog.customer_combo.setCurrentIndex(customer_index)

        study_texts = [dialog.study_combo.itemText(i) for i in range(dialog.study_combo.count())]
        assert "ST-100" in study_texts
        assert "ST-200" not in study_texts

        study_index = dialog.study_combo.findData(study.id)
        dialog.study_combo.setCurrentIndex(study_index)
        country_texts = [dialog.country_combo.itemText(i) for i in range(dialog.country_combo.count())]
        assert "Germany" in country_texts

        country_index = dialog.country_combo.findData(country.id)
        dialog.country_combo.setCurrentIndex(country_index)
        site_texts = [dialog.site_combo.itemText(i) for i in range(dialog.site_combo.count())]
        assert "S-001" in site_texts

        site_index = dialog.site_combo.findData(site.id)
        dialog.site_combo.setCurrentIndex(site_index)
        quote_texts = [dialog.quote_combo.itemText(i) for i in range(dialog.quote_combo.count())]
        assert "Q-001" in quote_texts

        quote_index = dialog.quote_combo.findData(quote.id)
        dialog.quote_combo.setCurrentIndex(quote_index)
        device_ids = {dialog.device_combo.itemData(i) for i in range(dialog.device_combo.count())}
        assert device.id in device_ids

    app.quit()
