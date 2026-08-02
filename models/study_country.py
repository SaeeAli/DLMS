from __future__ import annotations

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class StudyCountry(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    """Represents a country assignment scoped to a specific study."""

    __tablename__ = "study_countries"
    __table_args__ = (
        UniqueConstraint("study_id", "country_id", name="uq_study_country_pair"),
    )

    study_id: Mapped[str] = mapped_column(ForeignKey("studies.id"), nullable=False, index=True)
    country_id: Mapped[str] = mapped_column(ForeignKey("countries.id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="Active", index=True)
    notes: Mapped[str | None] = mapped_column(String(2000), nullable=True)

    study: Mapped["Study"] = relationship(back_populates="study_countries")
    country: Mapped["Country"] = relationship(back_populates="study_countries")
    sites: Mapped[list["Site"]] = relationship(back_populates="study_country", cascade="all, delete-orphan")
