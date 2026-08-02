from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Study(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    """Represents a study associated with a customer."""

    __tablename__ = "studies"

    study_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="Active", index=True)
    notes: Mapped[str | None] = mapped_column(String(2000), nullable=True)

    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.id"), nullable=False, index=True)

    customer: Mapped["Customer"] = relationship(back_populates="studies")
    study_countries: Mapped[list["StudyCountry"]] = relationship(
        back_populates="study",
        cascade="all, delete-orphan",
    )
