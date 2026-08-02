from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from database.base import Base
from models import (
    CalibrationCertificate,
    CalibrationJob,
    Country,
    Customer,
    Device,
    DeviceExchange,
    Quote,
    QuoteItem,
    Site,
    Study,
    StudyCountry,
    Supplier,
)


def test_models_create_and_link_relationships() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        customer = Customer(name="Acme Corp", contact_email="sales@example.com")
        study = Study(study_number="ST-001", customer=customer)
        country = Country(name="United Kingdom", country_code="GB")
        study_country = StudyCountry(study=study, country=country, status="Active")
        site = Site(name="North Site", site_number="NS-001", study_country=study_country)
        supplier = Supplier(name="Precision Instruments", supplier_code="PI-001", contact_email="support@example.com")
        device = Device(brand="Fluke", device_type="Multimeter", model="Model X", serial_number="SN-001", asset_number="AST-001")

        quote = Quote(site=site, status="Draft")
        quote_item = QuoteItem(quote=quote, device=device, quantity=2, unit_cost=75.0, unit_price=125.0)
        device_exchange = DeviceExchange(exchange_reference="EX-100", condition="Good")
        calibration_job = CalibrationJob(
            quote=quote,
            supplier=supplier,
            device_exchange=device_exchange,
            job_number="JOB-001",
            status="Scheduled",
        )
        calibration_certificate = CalibrationCertificate(
            calibration_job=calibration_job,
            certificate_number="CERT-001",
            issue_date=datetime(2024, 1, 16),
        )

        session.add_all([customer, study, country, study_country, site, supplier, device, quote, quote_item, device_exchange, calibration_job, calibration_certificate])
        session.commit()

        session.refresh(customer)
        session.refresh(quote)
        assert customer.studies[0].study_number == "ST-001"
        assert study.study_countries[0].country.country_code == "GB"
        assert study_country.sites[0].site_number == "NS-001"
        assert quote.quote_items[0].device is device
        assert quote.calibration_job is calibration_job
        assert calibration_job.device_exchange is device_exchange
        assert calibration_job.calibration_certificate is calibration_certificate
        assert calibration_job.supplier is supplier
        assert quote_item.line_profit == 100.0
