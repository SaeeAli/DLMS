from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Device(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    """Represents permanent device information for quotes and jobs."""

    __tablename__ = "devices"

    brand: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    device_type: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    model: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    serial_number: Mapped[str | None] = mapped_column(String(100), nullable=True, unique=True, index=True)
    asset_number: Mapped[str | None] = mapped_column(String(100), nullable=True, unique=True, index=True)

    quote_items: Mapped[list["QuoteItem"]] = relationship(back_populates="device", cascade="all, delete-orphan")

    @property
    def asset_tag(self) -> str | None:
        return self.asset_number

    @asset_tag.setter
    def asset_tag(self, value: str | None) -> None:
        self.asset_number = value
