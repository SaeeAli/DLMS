from __future__ import annotations

from models.calibration_job import CalibrationJob
from repositories.base_repository import BaseRepository


class CalibrationJobRepository(BaseRepository[CalibrationJob]):
    """Repository for CalibrationJob persistence operations."""

    def __init__(self, session) -> None:
        super().__init__(session, CalibrationJob)
