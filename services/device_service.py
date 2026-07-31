from __future__ import annotations

from models.device import Device
from repositories.device_repository import DeviceRepository
from services.base_service import BaseService


class DeviceService(BaseService[Device]):
    """Service for managing device records."""

    def __init__(self, repository: DeviceRepository) -> None:
        super().__init__(repository)

    def create_device(self, *, asset_tag: str, model: str | None = None, serial_number: str | None = None) -> Device:
        if not asset_tag or not asset_tag.strip():
            raise ValueError("asset_tag is required")

        device = Device(asset_tag=asset_tag.strip(), model=model.strip() if model else None, serial_number=serial_number.strip() if serial_number else None)
        return self.create(device)
