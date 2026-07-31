from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Calibration(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    """Represents a calibration event for a device."""

    __tablename__ = "calibrations"

    calibration_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    performed_by: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    remarks: Mapped[str | None] = mapped_column(String(2000), nullable=True)

    device_id: Mapped[str] = mapped_column(ForeignKey("devices.id"), nullable=False, index=True)

    device: Mapped["Device"] = relationship(back_populates="calibrations")
    certificate: Mapped["Certificate | None"] = relationship(back_populates="calibration", cascade="all, delete-orphan")
