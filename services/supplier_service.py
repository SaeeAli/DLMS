from __future__ import annotations

import re

from models.supplier import Supplier
from repositories.supplier_repository import SupplierRepository
from services.base_service import BaseService


class SupplierService(BaseService[Supplier]):
    """Service for managing supplier records."""

    SUPPORTED_CURRENCIES: tuple[str, ...] = ("EUR (€)", "USD ($)")
    EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

    def __init__(self, repository: SupplierRepository) -> None:
        super().__init__(repository)

    def create_supplier(
        self,
        *,
        name: str,
        country: str | None = None,
        city: str | None = None,
        address: str | None = None,
        contact_person: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        on_site_calibration: bool = False,
        exchange_device_available: bool = False,
        shipping_supported: bool = False,
        currency: str = "EUR (€)",
        default_calibration_lead_time_days: int = 1,
    ) -> Supplier:
        normalized_name = (name or "").strip()
        normalized_email = email.strip() if email else None
        normalized_currency = (currency or "").strip()
        self._validate_required_fields(name=normalized_name)
        self._validate_unique_supplier_name(name=normalized_name, existing_id=None)
        self._validate_email(email=normalized_email)
        self._validate_currency(currency=normalized_currency)
        self._validate_lead_time_days(default_calibration_lead_time_days)

        supplier = Supplier(
            name=normalized_name,
            country=country.strip() if country else None,
            city=city.strip() if city else None,
            address=address.strip() if address else None,
            contact_person=contact_person.strip() if contact_person else None,
            email=normalized_email,
            phone=phone.strip() if phone else None,
            on_site_calibration=on_site_calibration,
            exchange_device_available=exchange_device_available,
            shipping_supported=shipping_supported,
            currency=normalized_currency,
            default_calibration_lead_time_days=default_calibration_lead_time_days,
        )
        return self.create(supplier)

    def update_supplier(
        self,
        supplier: Supplier,
        *,
        name: str,
        country: str | None = None,
        city: str | None = None,
        address: str | None = None,
        contact_person: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        on_site_calibration: bool = False,
        exchange_device_available: bool = False,
        shipping_supported: bool = False,
        currency: str = "EUR (€)",
        default_calibration_lead_time_days: int = 1,
    ) -> Supplier:
        if supplier.id is None:
            raise ValueError("supplier id is required")

        normalized_name = (name or "").strip()
        normalized_email = email.strip() if email else None
        normalized_currency = (currency or "").strip()
        self._validate_required_fields(name=normalized_name)
        self._validate_unique_supplier_name(name=normalized_name, existing_id=supplier.id)
        self._validate_email(email=normalized_email)
        self._validate_currency(currency=normalized_currency)
        self._validate_lead_time_days(default_calibration_lead_time_days)

        supplier.name = normalized_name
        supplier.country = country.strip() if country else None
        supplier.city = city.strip() if city else None
        supplier.address = address.strip() if address else None
        supplier.contact_person = contact_person.strip() if contact_person else None
        supplier.email = normalized_email
        supplier.phone = phone.strip() if phone else None
        supplier.on_site_calibration = on_site_calibration
        supplier.exchange_device_available = exchange_device_available
        supplier.shipping_supported = shipping_supported
        supplier.currency = normalized_currency
        supplier.default_calibration_lead_time_days = default_calibration_lead_time_days
        return self.update(supplier)

    def delete_supplier(self, supplier: Supplier) -> None:
        if supplier.id is None:
            raise ValueError("supplier id is required")
        self.delete(supplier)

    def search_suppliers(self, query: str) -> list[Supplier]:
        if not query:
            return self.get_all()

        normalized = query.strip().lower()
        return [
            supplier
            for supplier in self.get_all()
            if normalized in supplier.name.lower()
            or normalized in (supplier.country or "").lower()
            or normalized in (supplier.contact_person or "").lower()
        ]

    def get_currency_options(self) -> list[str]:
        return list(self.SUPPORTED_CURRENCIES)

    def _validate_required_fields(self, *, name: str) -> None:
        if not name:
            raise ValueError("name is required")

    def _validate_unique_supplier_name(self, *, name: str, existing_id: str | None) -> None:
        normalized = name.lower()
        for supplier in self.get_all():
            if existing_id is not None and supplier.id == existing_id:
                continue
            if (supplier.name or "").strip().lower() == normalized:
                raise ValueError("A supplier with this name already exists")

    def _validate_email(self, *, email: str | None) -> None:
        if not email:
            return
        if not self.EMAIL_PATTERN.match(email):
            raise ValueError("email format is invalid")

    def _validate_currency(self, *, currency: str) -> None:
        if currency not in self.SUPPORTED_CURRENCIES:
            raise ValueError("currency must be one of: EUR (€), USD ($)")

    def _validate_lead_time_days(self, value: int) -> None:
        if not isinstance(value, int) or value <= 0:
            raise ValueError("default_calibration_lead_time_days must be a positive integer")
