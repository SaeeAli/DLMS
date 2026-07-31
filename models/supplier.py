from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Supplier(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    """Represents a supplier or manufacturer."""

    __tablename__ = "suppliers"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    supplier_code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    contact_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)

    devices: Mapped[list["Device"]] = relationship(back_populates="supplier", cascade="all, delete-orphan")
