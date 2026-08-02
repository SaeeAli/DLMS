from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class CalibrationJob(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    """Represents a calibration job linked to a quote and related artifacts."""

    __tablename__ = "calibration_jobs"

    job_number: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="Scheduled", index=True)
    scheduled_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    completed_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)

    quote_id: Mapped[str | None] = mapped_column(ForeignKey("quotes.id"), nullable=True, unique=True, index=True)
    device_exchange_id: Mapped[str | None] = mapped_column(ForeignKey("device_exchanges.id"), nullable=True, unique=True, index=True)
    calibration_certificate_id: Mapped[str | None] = mapped_column(ForeignKey("calibration_certificates.id"), nullable=True, unique=True, index=True)
    supplier_id: Mapped[str | None] = mapped_column(ForeignKey("suppliers.id"), nullable=True, index=True)

    quote: Mapped["Quote | None"] = relationship(back_populates="calibration_job")
    device_exchange: Mapped["DeviceExchange | None"] = relationship(back_populates="calibration_job")
    calibration_certificate: Mapped["CalibrationCertificate | None"] = relationship(
        back_populates="calibration_job",
        foreign_keys="[CalibrationCertificate.calibration_job_id]",
    )
    supplier: Mapped["Supplier | None"] = relationship(back_populates="calibration_jobs")
