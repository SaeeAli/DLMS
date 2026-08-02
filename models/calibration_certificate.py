from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class CalibrationCertificate(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    """Represents a calibration certificate issued for a job."""

    __tablename__ = "calibration_certificates"

    certificate_number: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    issue_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    file_reference: Mapped[str | None] = mapped_column(String(500), nullable=True)

    calibration_job_id: Mapped[str | None] = mapped_column(ForeignKey("calibration_jobs.id"), nullable=True, unique=True, index=True)

    calibration_job: Mapped["CalibrationJob | None"] = relationship(
        back_populates="calibration_certificate",
        foreign_keys="[CalibrationCertificate.calibration_job_id]",
    )
