from __future__ import annotations

from datetime import datetime

from models.calibration import Calibration
from repositories.calibration_repository import CalibrationRepository
from services.base_service import BaseService


class CalibrationService(BaseService[Calibration]):
    """Service for managing calibration records."""

    def __init__(self, repository: CalibrationRepository) -> None:
        super().__init__(repository)

    def create_calibration(self, *, device_id: str, calibration_date: datetime, performed_by: str | None = None) -> Calibration:
        if not device_id or not device_id.strip():
            raise ValueError("device_id is required")
        if not calibration_date:
            raise ValueError("calibration_date is required")

        calibration = Calibration(
            device_id=device_id.strip(),
            calibration_date=calibration_date,
            performed_by=performed_by.strip() if performed_by else None,
        )
        return self.create(calibration)
