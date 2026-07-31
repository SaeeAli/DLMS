from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Device(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    """Represents a calibrated device or instrument."""

    __tablename__ = "devices"

    asset_tag: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    serial_number: Mapped[str | None] = mapped_column(String(100), nullable=True, unique=True, index=True)
    model: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    manufacturer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    site_id: Mapped[str | None] = mapped_column(ForeignKey("sites.id"), nullable=True, index=True)
    supplier_id: Mapped[str | None] = mapped_column(ForeignKey("suppliers.id"), nullable=True, index=True)

    site: Mapped["Site | None"] = relationship(back_populates="devices")
    supplier: Mapped["Supplier | None"] = relationship(back_populates="devices")
    calibrations: Mapped[list["Calibration"]] = relationship(back_populates="device", cascade="all, delete-orphan")
