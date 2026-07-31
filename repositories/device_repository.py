from __future__ import annotations

from models.device import Device
from repositories.base_repository import BaseRepository


class DeviceRepository(BaseRepository[Device]):
    """Repository for Device persistence operations."""

    def __init__(self, session) -> None:
        super().__init__(session, Device)
