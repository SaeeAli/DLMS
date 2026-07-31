from __future__ import annotations

from datetime import datetime

from models.certificate import Certificate
from repositories.certificate_repository import CertificateRepository
from services.base_service import BaseService


class CertificateService(BaseService[Certificate]):
    """Service for managing certificate records."""

    def __init__(self, repository: CertificateRepository) -> None:
        super().__init__(repository)

    def create_certificate(self, *, calibration_id: str, certificate_number: str, issue_date: datetime | None = None) -> Certificate:
        if not calibration_id or not calibration_id.strip():
            raise ValueError("calibration_id is required")
        if not certificate_number or not certificate_number.strip():
            raise ValueError("certificate_number is required")

        certificate = Certificate(
            calibration_id=calibration_id.strip(),
            certificate_number=certificate_number.strip(),
            issue_date=issue_date,
        )
        return self.create(certificate)
