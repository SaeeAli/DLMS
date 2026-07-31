from __future__ import annotations

from models.site import Site
from repositories.base_repository import BaseRepository


class SiteRepository(BaseRepository[Site]):
    """Repository for Site persistence operations."""

    def __init__(self, session) -> None:
        super().__init__(session, Site)
