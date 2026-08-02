from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class QuoteItem(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    """Represents a line item in a quote."""

    __tablename__ = "quote_items"

    quantity: Mapped[int] = mapped_column(nullable=False, default=1)
    unit_cost: Mapped[float] = mapped_column(nullable=False, default=0.0)
    unit_price: Mapped[float] = mapped_column(nullable=False, default=0.0)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    quote_id: Mapped[str] = mapped_column(ForeignKey("quotes.id"), nullable=False, index=True)
    device_id: Mapped[str] = mapped_column(ForeignKey("devices.id"), nullable=False, index=True)

    quote: Mapped["Quote"] = relationship(back_populates="quote_items")
    device: Mapped["Device"] = relationship(back_populates="quote_items")

    @property
    def line_profit(self) -> float:
        return (self.unit_price - self.unit_cost) * self.quantity
