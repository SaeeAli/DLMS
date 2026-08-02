from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from models.mixins import UUIDPrimaryKeyMixin


class StudyCountry(Base, UUIDPrimaryKeyMixin):
    """Association table for studies and countries."""

    __tablename__ = "study_countries"

    study_id: Mapped[str] = mapped_column(ForeignKey("studies.id"), nullable=False, index=True)
    country_id: Mapped[str] = mapped_column(ForeignKey("countries.id"), nullable=False, index=True)
