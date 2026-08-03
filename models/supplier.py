from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Supplier(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    """Represents supplier information used across lifecycle modules."""

    __tablename__ = "suppliers"

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    country: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    city: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    contact_person: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    on_site_calibration: Mapped[bool] = mapped_column(nullable=False, default=False)
    exchange_device_available: Mapped[bool] = mapped_column(nullable=False, default=False)
    shipping_supported: Mapped[bool] = mapped_column(nullable=False, default=False)
    currency: Mapped[str] = mapped_column(String(20), nullable=False, default="EUR (€)")
    default_calibration_lead_time_days: Mapped[int] = mapped_column(nullable=False, default=1)

    calibration_jobs: Mapped[list["CalibrationJob"]] = relationship(back_populates="supplier", cascade="all, delete-orphan")
