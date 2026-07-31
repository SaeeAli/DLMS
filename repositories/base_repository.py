from __future__ import annotations

from typing import Generic, TypeVar

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Minimal repository abstraction for future implementations."""

    def __init__(self, session) -> None:
        self.session = session
