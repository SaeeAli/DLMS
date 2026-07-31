from __future__ import annotations

from models.calibration import Calibration
from repositories.base_repository import BaseRepository


class CalibrationRepository(BaseRepository[Calibration]):
    """Repository for Calibration persistence operations."""

    def __init__(self, session) -> None:
        super().__init__(session, Calibration)
