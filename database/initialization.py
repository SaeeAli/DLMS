from __future__ import annotations

from sqlalchemy import inspect

from utils.logging import get_logger

from database.base import Base
from database.engine import get_engine
from database.models import *  # noqa: F401,F403

logger = get_logger(__name__)


def initialize_database() -> None:
    """Create all database tables if they do not exist in an idempotent way."""
    engine = get_engine()

    # Import ORM models explicitly so the metadata is populated before table creation.
    # SQLAlchemy's create_all is safe to call repeatedly; it only creates missing tables.
    Base.metadata.create_all(bind=engine)

    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    expected_tables = set(Base.metadata.tables.keys())

    if expected_tables.issubset(existing_tables):
        logger.info(
            "Database initialization completed successfully; tables available: %s",
            ", ".join(sorted(expected_tables)),
        )
    else:
        logger.warning(
            "Database initialization completed with missing tables: %s",
            ", ".join(sorted(expected_tables - existing_tables)),
        )
