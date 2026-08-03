from __future__ import annotations

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class QuoteSite(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    """Join entity mapping one quote to one selected site."""

    __tablename__ = "quote_sites"
    __table_args__ = (
        UniqueConstraint("quote_id", "site_id", name="uq_quote_site_pair"),
    )

    quote_id: Mapped[str] = mapped_column(ForeignKey("quotes.id"), nullable=False, index=True)
    site_id: Mapped[str] = mapped_column(ForeignKey("sites.id"), nullable=False, index=True)

    quote: Mapped["Quote"] = relationship(back_populates="quote_sites")
    site: Mapped["Site"] = relationship(back_populates="quote_sites")