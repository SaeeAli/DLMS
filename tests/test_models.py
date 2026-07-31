from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from database.base import Base
from models import (
    Calibration,
    Certificate,
    Customer,
    Device,
    Site,
    Supplier,
)


def test_models_create_and_link_relationships() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        customer = Customer(name="Acme Corp", customer_code="ACM-001", contact_email="sales@example.com")
        site = Site(name="North Site", site_code="NS-001", customer=customer)
        supplier = Supplier(name="Precision Instruments", supplier_code="PI-001", contact_email="support@example.com")
        device = Device(asset_tag="AST-001", serial_number="SN-001", model="Model X", site=site, supplier=supplier)
        calibration = Calibration(device=device, calibration_date=datetime(2024, 1, 15), performed_by="Lab One")
        certificate = Certificate(
            calibration=calibration,
            certificate_number="CERT-001",
            issue_date=datetime(2024, 1, 16),
        )

        session.add_all([customer, site, supplier, device, calibration, certificate])
        session.commit()

        session.refresh(customer)
        assert customer.sites[0].site_code == "NS-001"
        assert device.site is site
        assert calibration.certificate is certificate
