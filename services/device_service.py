from __future__ import annotations

from models.device import Device
from repositories.device_repository import DeviceRepository
from services.base_service import BaseService


class DeviceService(BaseService[Device]):
    """Service for managing device records."""

    def __init__(self, repository: DeviceRepository) -> None:
        super().__init__(repository)

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
        identifier = (asset_tag or asset_number or "").strip()
        self._validate_required_fields(asset_tag=identifier)
        self._validate_unique_serial_number(serial_number=serial_number, existing_id=None)

        device = Device(
            brand=brand.strip() if brand else None,
            device_type=device_type.strip() if device_type else None,
            model=model.strip() if model else None,
            serial_number=serial_number.strip() if serial_number else None,
            asset_number=identifier,
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

        identifier = (asset_tag or asset_number or device.asset_number or "").strip()
        self._validate_required_fields(asset_tag=identifier)
        self._validate_unique_serial_number(serial_number=serial_number, existing_id=device.id)

        device.brand = brand.strip() if brand else None
        device.device_type = device_type.strip() if device_type else None
        device.model = model.strip() if model else None
        device.serial_number = serial_number.strip() if serial_number else None
        device.asset_number = identifier or None
        return self.update(device)

    def delete_device(self, device: Device) -> None:
        if device.id is None:
            raise ValueError("device id is required")
        self.delete(device)

    def _validate_required_fields(self, *, asset_tag: str) -> None:
        if not asset_tag or not asset_tag.strip():
            raise ValueError("Device name is required")

    def _validate_unique_serial_number(self, *, serial_number: str | None, existing_id: str | None) -> None:
        if not serial_number or not serial_number.strip():
            return

        normalized_serial = serial_number.strip()
        for existing in self.get_all():
            if existing.id == existing_id:
                continue
            if (existing.serial_number or "").strip() == normalized_serial:
                raise ValueError("A device with this serial number already exists")
