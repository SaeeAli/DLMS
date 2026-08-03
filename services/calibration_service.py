from __future__ import annotations

from datetime import datetime

from models.calibration import Calibration, CalibrationStatus
from models.country import Country
from models.customer import Customer
from models.device import Device
from models.quote import Quote
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
from services.base_service import BaseService


class CalibrationService(BaseService[Calibration]):
    """Service for managing calibration records."""

    def __init__(
        self,
        repository: CalibrationRepository,
        customer_repository: CustomerRepository,
        study_repository: StudyRepository,
        study_country_repository: StudyCountryRepository,
        country_repository: CountryRepository,
        site_repository: SiteRepository,
        quote_repository: QuoteRepository,
        device_repository: DeviceRepository,
        supplier_repository: SupplierRepository,
    ) -> None:
        super().__init__(repository)
        self.customer_repository = customer_repository
        self.study_repository = study_repository
        self.study_country_repository = study_country_repository
        self.country_repository = country_repository
        self.site_repository = site_repository
        self.quote_repository = quote_repository
        self.device_repository = device_repository
        self.supplier_repository = supplier_repository

    def create_calibration(
        self,
        *,
        customer_id: str,
        study_id: str,
        country_id: str,
        site_id: str,
        quote_id: str,
        device_id: str,
        supplier_id: str,
        calibration_start_date: datetime,
        calibration_cycle_months: int,
        calibration_due_date: datetime,
        outbound_tracking_number: str | None = None,
        delivery_date: datetime | None = None,
        delivery_confirmed: bool = False,
        return_tracking_number: str | None = None,
        return_received_date: datetime | None = None,
        status: str = CalibrationStatus.PENDING.value,
    ) -> Calibration:
        self._validate_required_relations(
            customer_id=customer_id,
            study_id=study_id,
            country_id=country_id,
            site_id=site_id,
            quote_id=quote_id,
            device_id=device_id,
            supplier_id=supplier_id,
        )
        self._validate_fields(
            calibration_start_date=calibration_start_date,
            calibration_cycle_months=calibration_cycle_months,
            calibration_due_date=calibration_due_date,
            status=status,
        )

        calibration = Calibration(
            customer_id=customer_id.strip(),
            study_id=study_id.strip(),
            country_id=country_id.strip(),
            site_id=site_id.strip(),
            quote_id=quote_id.strip(),
            device_id=device_id.strip(),
            supplier_id=supplier_id.strip(),
            calibration_start_date=calibration_start_date,
            calibration_cycle_months=calibration_cycle_months,
            calibration_due_date=calibration_due_date,
            outbound_tracking_number=outbound_tracking_number.strip() if outbound_tracking_number else None,
            delivery_date=delivery_date,
            delivery_confirmed=delivery_confirmed,
            return_tracking_number=return_tracking_number.strip() if return_tracking_number else None,
            return_received_date=return_received_date,
            status=status,
        )
        return self.create(calibration)

    def update_calibration(
        self,
        calibration: Calibration,
        *,
        customer_id: str,
        study_id: str,
        country_id: str,
        site_id: str,
        quote_id: str,
        device_id: str,
        supplier_id: str,
        calibration_start_date: datetime,
        calibration_cycle_months: int,
        calibration_due_date: datetime,
        outbound_tracking_number: str | None = None,
        delivery_date: datetime | None = None,
        delivery_confirmed: bool = False,
        return_tracking_number: str | None = None,
        return_received_date: datetime | None = None,
        status: str = CalibrationStatus.PENDING.value,
    ) -> Calibration:
        if calibration.id is None:
            raise ValueError("calibration id is required")

        self._validate_required_relations(
            customer_id=customer_id,
            study_id=study_id,
            country_id=country_id,
            site_id=site_id,
            quote_id=quote_id,
            device_id=device_id,
            supplier_id=supplier_id,
        )
        self._validate_fields(
            calibration_start_date=calibration_start_date,
            calibration_cycle_months=calibration_cycle_months,
            calibration_due_date=calibration_due_date,
            status=status,
        )

        calibration.customer_id = customer_id.strip()
        calibration.study_id = study_id.strip()
        calibration.country_id = country_id.strip()
        calibration.site_id = site_id.strip()
        calibration.quote_id = quote_id.strip()
        calibration.device_id = device_id.strip()
        calibration.supplier_id = supplier_id.strip()
        calibration.calibration_start_date = calibration_start_date
        calibration.calibration_cycle_months = calibration_cycle_months
        calibration.calibration_due_date = calibration_due_date
        calibration.outbound_tracking_number = outbound_tracking_number.strip() if outbound_tracking_number else None
        calibration.delivery_date = delivery_date
        calibration.delivery_confirmed = delivery_confirmed
        calibration.return_tracking_number = return_tracking_number.strip() if return_tracking_number else None
        calibration.return_received_date = return_received_date
        calibration.status = status
        return self.update(calibration)

    def delete_calibration(self, calibration: Calibration) -> None:
        if calibration.id is None:
            raise ValueError("calibration id is required")
        self.delete(calibration)

    def search_calibrations(self, query: str) -> list[Calibration]:
        if not query:
            return self.get_all()

        normalized = query.strip().lower()
        return [
            calibration
            for calibration in self.get_all()
            if normalized in (calibration.customer.name or "").lower()
            or normalized in (calibration.study.study_number or "").lower()
            or normalized in (calibration.country.name or "").lower()
            or normalized in (calibration.site.site_number or "").lower()
            or normalized in (calibration.quote.quote_number or "").lower()
            or normalized in (calibration.device.serial_number or "").lower()
            or normalized in (calibration.supplier.name or "").lower()
            or normalized in (calibration.status or "").lower()
        ]

    def get_status_options(self) -> list[str]:
        return [status.value for status in CalibrationStatus]

    def get_customer_options(self) -> list[Customer]:
        return self.customer_repository.get_all()

    def get_study_options(self, customer_id: str | None) -> list[Study]:
        if not customer_id:
            return []
        return [study for study in self.study_repository.get_all() if study.customer_id == customer_id]

    def get_country_options(self, study_id: str | None) -> list[Country]:
        if not study_id:
            return []
        countries: list[Country] = []
        for assignment in self._study_country_options(study_id=study_id):
            if assignment.country is not None:
                countries.append(assignment.country)
        return countries

    def get_site_options(self, study_id: str | None, country_id: str | None) -> list[Site]:
        if not study_id or not country_id:
            return []

        valid_assignment_ids = {
            assignment.id
            for assignment in self._study_country_options(study_id=study_id)
            if assignment.country_id == country_id and assignment.id is not None
        }
        if not valid_assignment_ids:
            return []

        return [site for site in self.site_repository.get_all() if site.study_country_id in valid_assignment_ids]

    def get_quote_options(self, site_id: str | None) -> list[Quote]:
        if not site_id:
            return []
        return [
            quote
            for quote in self.quote_repository.get_all()
            if any(quote_site.site_id == site_id for quote_site in quote.quote_sites)
        ]

    def get_device_options(self, quote_id: str | None) -> list[Device]:
        if not quote_id:
            return []

        quote = self.quote_repository.get_by_id(quote_id)
        if quote is None:
            return []

        devices: list[Device] = []
        seen_ids: set[str] = set()
        for item in quote.quote_items:
            device = item.device
            if device is None or device.id is None or device.id in seen_ids:
                continue
            seen_ids.add(device.id)
            devices.append(device)
        return devices

    def get_supplier_options(self) -> list[Supplier]:
        return self.supplier_repository.get_all()

    def _study_country_options(self, *, study_id: str) -> list[StudyCountry]:
        return [assignment for assignment in self.study_country_repository.get_all() if assignment.study_id == study_id]

    def _validate_required_relations(
        self,
        *,
        customer_id: str,
        study_id: str,
        country_id: str,
        site_id: str,
        quote_id: str,
        device_id: str,
        supplier_id: str,
    ) -> None:
        if not customer_id or not customer_id.strip():
            raise ValueError("customer_id is required")
        if not study_id or not study_id.strip():
            raise ValueError("study_id is required")
        if not country_id or not country_id.strip():
            raise ValueError("country_id is required")
        if not site_id or not site_id.strip():
            raise ValueError("site_id is required")
        if not quote_id or not quote_id.strip():
            raise ValueError("quote_id is required")
        if not device_id or not device_id.strip():
            raise ValueError("device_id is required")
        if not supplier_id or not supplier_id.strip():
            raise ValueError("supplier_id is required")

    def _validate_fields(
        self,
        *,
        calibration_start_date: datetime,
        calibration_cycle_months: int,
        calibration_due_date: datetime,
        status: str,
    ) -> None:
        if calibration_start_date is None:
            raise ValueError("calibration_start_date is required")
        if calibration_cycle_months <= 0:
            raise ValueError("calibration_cycle_months must be a positive integer")
        if calibration_due_date is None:
            raise ValueError("calibration_due_date is required")
        if status not in self.get_status_options():
            raise ValueError("status is invalid")
