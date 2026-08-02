from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from models.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from models.study_country import StudyCountry


class Study(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    """Represents a study associated with a customer."""

    __tablename__ = "studies"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    study_code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String(2000), nullable=True)

    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.id"), nullable=False, index=True)

    customer: Mapped["Customer"] = relationship(back_populates="studies")
    countries: Mapped[list["Country"]] = relationship(
        "Country",
        secondary=StudyCountry.__tablename__,
        back_populates="studies",
        cascade="save-update,merge",
    )
