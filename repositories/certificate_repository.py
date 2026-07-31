from __future__ import annotations

from models.certificate import Certificate
from repositories.base_repository import BaseRepository


class CertificateRepository(BaseRepository[Certificate]):
    """Repository for Certificate persistence operations."""

    def __init__(self, session) -> None:
        super().__init__(session, Certificate)
