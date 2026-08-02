from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class DeviceExchange(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    """Represents a device exchange linked to a calibration job."""

    __tablename__ = "device_exchanges"

    exchange_reference: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    condition: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(2000), nullable=True)

    calibration_job: Mapped["CalibrationJob | None"] = relationship(back_populates="device_exchange")
