from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class BaseModel(DeclarativeBase):
    """Shared declarative base for application models."""
