from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from database.base import Base
from models.calibration import Calibration, CalibrationStatus
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


def _seed_entities(session: Session):
    customer = Customer(name="Acme")
    study = Study(study_number="ST-100", customer=customer)
    country = Country(name="Germany")
    assignment = StudyCountry(study=study, country=country)
    site = Site(name="Berlin Site", site_number="S-001", study_country=assignment)
    device = Device(brand="Fluke", device_type="Thermometer", model="T300", serial_number="SN-100", asset_number="Fluke")
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

    session.add_all([customer, study, country, assignment, site, device, supplier, quote, quote_item])
    session.flush()
    return customer, study, country, site, quote, device, supplier


def test_calibration_repository_persists_full_record() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        customer, study, country, site, quote, device, supplier = _seed_entities(session)
        repository = CalibrationRepository(session)

        created = repository.create(
            Calibration(
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
                outbound_tracking_number="OUT-100",
                delivery_date=datetime(2026, 2, 2, tzinfo=timezone.utc),
                delivery_confirmed=True,
                return_tracking_number="RET-200",
                return_received_date=datetime(2026, 2, 20, tzinfo=timezone.utc),
                status=CalibrationStatus.PENDING.value,
            )
        )

        assert created.id is not None
        fetched = repository.get_by_id(created.id)
        assert fetched is not None
        assert fetched.customer_id == customer.id
        assert fetched.study_id == study.id
        assert fetched.country_id == country.id
        assert fetched.site_id == site.id
        assert fetched.quote_id == quote.id
        assert fetched.device_id == device.id
        assert fetched.supplier_id == supplier.id
        assert fetched.status == CalibrationStatus.PENDING.value
