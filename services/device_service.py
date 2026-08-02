from __future__ import annotations

from models.device import Device
from repositories.device_repository import DeviceRepository
from services.base_service import BaseService


class DeviceService(BaseService[Device]):
    """Service for managing device records."""

    DEFAULT_DEVICE_TYPES: tuple[str, ...] = (
        "Centrifuge",
        "ECG",
        "Freezer",
        "Refrigerator",
        "Incubator",
        "Infusion Pump",
        "Syringe Pump",
        "Temperature Logger",
        "Pipette",
        "Balance",
        "Blood Pressure Monitor",
        "Thermometer",
        "Defibrillator",
        "Other",
    )

    def __init__(self, repository: DeviceRepository) -> None:
        super().__init__(repository)
        self._migrate_legacy_device_name_to_brand()

    def create_device(
        self,
        *,
        asset_tag: str | None = None,
        asset_number: str | None = None,
        brand: str | None = None,
        device_type: str | None = None,
        model: str | None = None,
        serial_number: str | None = None,
    ) -> Device:
        normalized_brand = (brand or asset_tag or asset_number or "").strip()
        normalized_type = (device_type or "").strip()
        self._validate_required_fields(brand=normalized_brand, device_type=normalized_type)
        self._validate_unique_serial_number(serial_number=serial_number, existing_id=None)

        device = Device(
            brand=normalized_brand,
            device_type=normalized_type,
            model=model.strip() if model else None,
            serial_number=serial_number.strip() if serial_number else None,
            asset_number=normalized_brand,
        )
        return self.create(device)

    def update_device(
        self,
        device: Device,
        *,
        asset_tag: str | None = None,
        asset_number: str | None = None,
        brand: str | None = None,
        device_type: str | None = None,
        model: str | None = None,
        serial_number: str | None = None,
    ) -> Device:
        if device.id is None:
            raise ValueError("device id is required")

        normalized_brand = (brand or asset_tag or asset_number or device.brand or device.asset_number or "").strip()
        normalized_type = (device_type or device.device_type or "").strip()
        self._validate_required_fields(brand=normalized_brand, device_type=normalized_type)
        self._validate_unique_serial_number(serial_number=serial_number, existing_id=device.id)

        device.brand = normalized_brand
        device.device_type = normalized_type
        device.model = model.strip() if model else None
        device.serial_number = serial_number.strip() if serial_number else None
        device.asset_number = normalized_brand
        return self.update(device)

    def delete_device(self, device: Device) -> None:
        if device.id is None:
            raise ValueError("device id is required")
        self.delete(device)

    def get_device_type_options(self) -> list[str]:
        """Return available device types; can later source from a master data repository."""
        return list(self.DEFAULT_DEVICE_TYPES)

    def _validate_required_fields(self, *, brand: str, device_type: str) -> None:
        if not brand or not brand.strip():
            raise ValueError("brand is required")
        if not device_type or not device_type.strip():
            raise ValueError("device_type is required")

    def _validate_unique_serial_number(self, *, serial_number: str | None, existing_id: str | None) -> None:
        if not serial_number or not serial_number.strip():
            return

        normalized_serial = serial_number.strip()
        for existing in self.get_all():
            if existing.id == existing_id:
                continue
            if (existing.serial_number or "").strip() == normalized_serial:
                raise ValueError("A device with this serial number already exists")

    def _migrate_legacy_device_name_to_brand(self) -> None:
        migrated = False
        for device in self.get_all():
            if device.brand and device.brand.strip():
                continue
            legacy_name = (device.asset_number or "").strip()
            if not legacy_name:
                continue
            device.brand = legacy_name
            device.asset_number = legacy_name
            migrated = True

        if migrated:
            # Keep migration local to this service session; caller transaction rules still apply.
            self.repository.session.flush()
