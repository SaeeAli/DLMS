from __future__ import annotations

from models.quote_item import QuoteItem
from repositories.base_repository import BaseRepository


class QuoteItemRepository(BaseRepository[QuoteItem]):
    """Repository for QuoteItem persistence operations."""

    def __init__(self, session) -> None:
        super().__init__(session, QuoteItem)
