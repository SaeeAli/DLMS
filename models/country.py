from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Country(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    """Represents a country that can be linked to many studies."""

    __tablename__ = "countries"

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    country_code: Mapped[str | None] = mapped_column(String(10), nullable=True, unique=True, index=True)

    study_countries: Mapped[list["StudyCountry"]] = relationship(
        back_populates="country",
        cascade="all, delete-orphan",
    )
