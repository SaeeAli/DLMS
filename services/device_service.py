from __future__ import annotations

from models.device import Device
from repositories.device_repository import DeviceRepository
from services.base_service import BaseService


class DeviceService(BaseService[Device]):
    """Service for managing device records."""

    def __init__(self, repository: DeviceRepository) -> None:
        super().__init__(repository)

    def create_device(self, *, asset_tag: str, model: str | None = None, serial_number: str | None = None) -> Device:
        self._validate_required_fields(asset_tag=asset_tag)
        self._validate_unique_serial_number(serial_number=serial_number, existing_id=None)

        device = Device(
            asset_tag=asset_tag.strip(),
            model=model.strip() if model else None,
            serial_number=serial_number.strip() if serial_number else None,
        )
        return self.create(device)

    def update_device(self, device: Device, *, asset_tag: str, model: str | None = None, serial_number: str | None = None) -> Device:
        if device.id is None:
            raise ValueError("device id is required")

        self._validate_required_fields(asset_tag=asset_tag)
        self._validate_unique_serial_number(serial_number=serial_number, existing_id=device.id)

        device.asset_tag = asset_tag.strip()
        device.model = model.strip() if model else None
        device.serial_number = serial_number.strip() if serial_number else None
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
