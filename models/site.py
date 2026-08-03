from __future__ import annotations

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Site(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    """Represents a site belonging to exactly one study-country assignment."""

    __tablename__ = "sites"
    __table_args__ = (
        UniqueConstraint("study_country_id", "site_number", name="uq_site_number_per_study_country"),
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    site_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    city: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="Active", index=True)
    notes: Mapped[str | None] = mapped_column(String(2000), nullable=True)

    study_country_id: Mapped[str] = mapped_column(ForeignKey("study_countries.id"), nullable=False, index=True)

    study_country: Mapped["StudyCountry"] = relationship(back_populates="sites")
    quote_sites: Mapped[list["QuoteSite"]] = relationship(back_populates="site", cascade="all, delete-orphan")

    @property
    def site_code(self) -> str:
        return self.site_number

    @site_code.setter
    def site_code(self, value: str) -> None:
        self.site_number = value
