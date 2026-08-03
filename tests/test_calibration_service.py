from datetime import datetime, timezone

import pytest
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
    return customer, study, country, site, quote, device, supplier, customer_two, study_two, country_two, site_two, quote_two, device_two


def test_calibration_service_create_search_update_delete() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        service = _make_service(session)
        customer, study, country, site, quote, device, supplier, *_ = _seed_entities(session)

        created = service.create_calibration(
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
        assert created.id is not None

        assert len(service.search_calibrations("acme")) == 1
        assert len(service.search_calibrations("q-001")) == 1

        updated = service.update_calibration(
            created,
            customer_id=customer.id,
            study_id=study.id,
            country_id=country.id,
            site_id=site.id,
            quote_id=quote.id,
            device_id=device.id,
            supplier_id=supplier.id,
            calibration_start_date=datetime(2026, 2, 1, tzinfo=timezone.utc),
            calibration_cycle_months=24,
            calibration_due_date=datetime(2028, 2, 1, tzinfo=timezone.utc),
            status=CalibrationStatus.CLOSED.value,
        )
        assert updated.calibration_cycle_months == 24
        assert updated.status == CalibrationStatus.CLOSED.value

        service.delete_calibration(updated)
        assert service.get_by_id(created.id) is None


def test_calibration_service_validations_and_cascading_options() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        service = _make_service(session)
        customer, study, country, site, quote, device, supplier, customer_two, study_two, country_two, site_two, quote_two, device_two = _seed_entities(session)

        with pytest.raises(ValueError, match="customer_id is required"):
            service.create_calibration(
                customer_id="",
                study_id=study.id,
                country_id=country.id,
                site_id=site.id,
                quote_id=quote.id,
                device_id=device.id,
                supplier_id=supplier.id,
                calibration_start_date=datetime(2026, 2, 1, tzinfo=timezone.utc),
                calibration_cycle_months=12,
                calibration_due_date=datetime(2027, 2, 1, tzinfo=timezone.utc),
            )

        with pytest.raises(ValueError, match="status is invalid"):
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
                status="BadStatus",
            )

        studies = service.get_study_options(customer.id)
        assert [item.id for item in studies] == [study.id]

        countries = service.get_country_options(study.id)
        assert [item.id for item in countries] == [country.id]

        sites = service.get_site_options(study.id, country.id)
        assert [item.id for item in sites] == [site.id]

        quotes = service.get_quote_options(site.id)
        assert [item.id for item in quotes] == [quote.id]

        devices = service.get_device_options(quote.id)
        assert [item.id for item in devices] == [device.id]

        other_quotes = service.get_quote_options(site_two.id)
        assert [item.id for item in other_quotes] == [quote_two.id]

        other_devices = service.get_device_options(quote_two.id)
        assert [item.id for item in other_devices] == [device_two.id]

        suppliers = service.get_supplier_options()
        supplier_ids = {item.id for item in suppliers}
        assert supplier.id in supplier_ids

        statuses = service.get_status_options()
        assert statuses[0] == CalibrationStatus.PENDING.value
        assert CalibrationStatus.CLOSED.value in statuses
