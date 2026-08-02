from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from models.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from models.study_country import StudyCountry


class Country(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    """Represents a country used by studies and sites."""

    __tablename__ = "countries"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    country_code: Mapped[str] = mapped_column(String(10), nullable=False, unique=True, index=True)

    studies: Mapped[list["Study"]] = relationship(
        "Study",
        secondary=StudyCountry.__tablename__,
        back_populates="countries",
        cascade="save-update,merge",
    )
    sites: Mapped[list["Site"]] = relationship(back_populates="country", cascade="all, delete-orphan")
