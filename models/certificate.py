from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Certificate(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    """Represents an issued calibration certificate."""

    __tablename__ = "certificates"

    certificate_number: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    issue_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    file_reference: Mapped[str | None] = mapped_column(String(500), nullable=True)

    calibration_id: Mapped[str] = mapped_column(ForeignKey("calibrations.id"), nullable=False, unique=True, index=True)

    calibration: Mapped["Calibration"] = relationship(back_populates="certificate")
