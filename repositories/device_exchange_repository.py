from __future__ import annotations

from models.device_exchange import DeviceExchange
from repositories.base_repository import BaseRepository


class DeviceExchangeRepository(BaseRepository[DeviceExchange]):
    """Repository for DeviceExchange persistence operations."""

    def __init__(self, session) -> None:
        super().__init__(session, DeviceExchange)
