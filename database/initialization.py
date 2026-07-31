from __future__ import annotations

from utils.logging import get_logger

from database.base import Base
from database.engine import get_engine

logger = get_logger(__name__)


def initialize_database() -> None:
    """Create all database tables if they do not exist."""
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialization completed")
