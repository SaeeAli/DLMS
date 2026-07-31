"""Database foundation package for DLMS."""

from database.base import Base
from database.engine import get_engine

__all__ = [
    "Base",
    "SessionLocal",
    "get_engine",
    "get_session",
    "initialize_database",
    "session_scope",
]


def initialize_database() -> None:
    from database.initialization import initialize_database as _initialize_database

    return _initialize_database()


def get_session():
    from database.session import get_session as _get_session

    return _get_session()


def session_scope():
    from database.session import session_scope as _session_scope

    return _session_scope()


SessionLocal = None
try:
    from database.session import SessionLocal as _SessionLocal

    SessionLocal = _SessionLocal
except Exception:  # pragma: no cover - import-time guard for circular init
    SessionLocal = None
