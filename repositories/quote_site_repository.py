from __future__ import annotations

from models.quote_site import QuoteSite
from repositories.base_repository import BaseRepository


class QuoteSiteRepository(BaseRepository[QuoteSite]):
    """Repository for QuoteSite persistence operations."""

    def __init__(self, session) -> None:
        super().__init__(session, QuoteSite)