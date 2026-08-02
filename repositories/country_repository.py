from __future__ import annotations

from models.country import Country
from repositories.base_repository import BaseRepository


class CountryRepository(BaseRepository[Country]):
    """Repository for Country persistence operations."""

    def __init__(self, session) -> None:
        super().__init__(session, Country)
