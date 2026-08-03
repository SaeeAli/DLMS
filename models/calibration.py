from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class CalibrationStatus(str, Enum):
    PENDING = "Pending"
    REPLACEMENT_DEVICE_PREPARING = "ReplacementDevicePreparing"
    REPLACEMENT_DEVICE_SHIPPED = "ReplacementDeviceShipped"
    DELIVERED_TO_SITE = "DeliveredToSite"
    OLD_DEVICE_IN_TRANSIT = "OldDeviceInTransit"
    OLD_DEVICE_RECEIVED = "OldDeviceReceived"
    CALIBRATION_COMPLETED = "CalibrationCompleted"
    CERTIFICATE_UPLOADED = "CertificateUploaded"
    CLOSED = "Closed"


class Calibration(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    """Represents one calibration lifecycle record for a device."""

    __tablename__ = "calibrations"

    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.id"), nullable=False, index=True)
    study_id: Mapped[str] = mapped_column(ForeignKey("studies.id"), nullable=False, index=True)
    country_id: Mapped[str] = mapped_column(ForeignKey("countries.id"), nullable=False, index=True)
    site_id: Mapped[str] = mapped_column(ForeignKey("sites.id"), nullable=False, index=True)
    quote_id: Mapped[str] = mapped_column(ForeignKey("quotes.id"), nullable=False, index=True)
    device_id: Mapped[str] = mapped_column(ForeignKey("devices.id"), nullable=False, index=True)
    supplier_id: Mapped[str] = mapped_column(ForeignKey("suppliers.id"), nullable=False, index=True)

    calibration_start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    calibration_cycle_months: Mapped[int] = mapped_column(nullable=False, default=12)
    calibration_due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    outbound_tracking_number: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    delivery_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    delivery_confirmed: Mapped[bool] = mapped_column(nullable=False, default=False)

    return_tracking_number: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    return_received_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)

    status: Mapped[str] = mapped_column(String(64), nullable=False, default=CalibrationStatus.PENDING.value, index=True)

    customer: Mapped["Customer"] = relationship()
    study: Mapped["Study"] = relationship()
    country: Mapped["Country"] = relationship()
    site: Mapped["Site"] = relationship()
    quote: Mapped["Quote"] = relationship()
    supplier: Mapped["Supplier"] = relationship()

    device: Mapped["Device"] = relationship()
    certificate: Mapped["Certificate | None"] = relationship(
        foreign_keys="[Certificate.calibration_id]",
    )
