from __future__ import annotations

from models.calibration_certificate import CalibrationCertificate
from repositories.base_repository import BaseRepository


class CalibrationCertificateRepository(BaseRepository[CalibrationCertificate]):
    """Repository for CalibrationCertificate persistence operations."""

    def __init__(self, session) -> None:
        super().__init__(session, CalibrationCertificate)
