from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Quote(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    """Represents a quote for one study-country context across one or more sites."""

    __tablename__ = "quotes"

    quote_number: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    quote_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="Draft", index=True)
    approval_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    notes: Mapped[str | None] = mapped_column(String(2000), nullable=True)

    quote_sites: Mapped[list["QuoteSite"]] = relationship(back_populates="quote", cascade="all, delete-orphan")
    quote_items: Mapped[list["QuoteItem"]] = relationship(back_populates="quote", cascade="all, delete-orphan")
    calibration_job: Mapped["CalibrationJob | None"] = relationship(back_populates="quote", cascade="all, delete-orphan")
