from __future__ import annotations

from models.quote import Quote
from repositories.base_repository import BaseRepository


class QuoteRepository(BaseRepository[Quote]):
    """Repository for Quote persistence operations."""

    def __init__(self, session) -> None:
        super().__init__(session, Quote)
