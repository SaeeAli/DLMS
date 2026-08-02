from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Quote(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    """Represents an immutable quote for a site."""

    __tablename__ = "quotes"

    quote_number: Mapped[str | None] = mapped_column(String(100), nullable=True, unique=True, index=True)
    quote_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="Draft", index=True)
    approval_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)

    site_id: Mapped[str] = mapped_column(ForeignKey("sites.id"), nullable=False, index=True)

    site: Mapped["Site"] = relationship(back_populates="quotes")
    quote_items: Mapped[list["QuoteItem"]] = relationship(back_populates="quote", cascade="all, delete-orphan")
    calibration_job: Mapped["CalibrationJob | None"] = relationship(back_populates="quote", cascade="all, delete-orphan")
