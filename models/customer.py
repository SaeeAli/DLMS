from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Customer(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    """Represents a customer organization."""

    __tablename__ = "customers"
    __table_args__ = (
        {"sqlite_autoincrement": True},
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    customer_code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    contact_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)

    studies: Mapped[list["Study"]] = relationship(back_populates="customer", cascade="all, delete-orphan")
    sites: Mapped[list["Site"]] = relationship(back_populates="customer", cascade="all, delete-orphan")
