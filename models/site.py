from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Site(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    """Represents a physical site belonging to a customer."""

    __tablename__ = "sites"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    site_code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    city: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)

    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.id"), nullable=False, index=True)
    country_id: Mapped[str | None] = mapped_column(ForeignKey("countries.id"), nullable=True, index=True)

    customer: Mapped["Customer"] = relationship(back_populates="sites")
    country: Mapped["Country | None"] = relationship(back_populates="sites")
    quotes: Mapped[list["Quote"]] = relationship(back_populates="site", cascade="all, delete-orphan")
