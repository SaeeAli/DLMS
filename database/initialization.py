from __future__ import annotations

from sqlalchemy import inspect

from utils.logging import get_logger

from database.base import Base
from database.engine import get_engine
from database.models import *  # noqa: F401,F403

logger = get_logger(__name__)


def initialize_database() -> None:
    """Create all database tables and rebuild them when the schema shape has changed."""
    engine = get_engine()

    # Import ORM models explicitly so the metadata is populated before table creation.
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    expected_tables = set(Base.metadata.tables.keys())

    if not expected_tables.issubset(existing_tables):
        logger.info("Creating missing database tables: %s", ", ".join(sorted(expected_tables - existing_tables)))
        Base.metadata.create_all(bind=engine)
    elif _schema_requires_rebuild(engine, inspector):
        logger.warning("Detected a schema mismatch; rebuilding database tables")
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
    else:
        logger.info(
            "Database initialization completed successfully; tables available: %s",
            ", ".join(sorted(expected_tables)),
        )
        return

    logger.info("Database initialization completed successfully; tables available: %s", ", ".join(sorted(expected_tables)))


def _schema_requires_rebuild(engine, inspector) -> bool:
    """Return True when the existing SQLite tables do not match the ORM column definitions."""
    for table_name in Base.metadata.tables:
        if table_name not in inspector.get_table_names():
            return True

        expected_columns = {column.name for column in Base.metadata.tables[table_name].columns}
        actual_columns = {column["name"] for column in inspector.get_columns(table_name)}
        if expected_columns != actual_columns:
            return True

    return False
