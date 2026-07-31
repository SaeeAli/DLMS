from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from utils.logging import get_logger

logger = get_logger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_DATABASE_URL = f"sqlite:///{(DATA_DIR / 'dlms.sqlite3').resolve().as_posix()}"

_engine: Optional[Engine] = None


def get_database_url() -> str:
    """Return the configured SQLite database URL."""
    return os.getenv("DLMS_DATABASE_URL", DEFAULT_DATABASE_URL)


def get_engine() -> Engine:
    """Return a singleton SQLAlchemy engine for the application."""
    global _engine
    if _engine is None:
        connect_args = {"check_same_thread": False} if get_database_url().startswith("sqlite") else {}
        _engine = create_engine(
            get_database_url(),
            connect_args=connect_args,
            echo=os.getenv("DLMS_SQLALCHEMY_ECHO", "0") == "1",
            future=True,
        )
        logger.info("Initialized database engine for %s", get_database_url())
    return _engine
