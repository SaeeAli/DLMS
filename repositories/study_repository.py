from __future__ import annotations

from models.study import Study
from repositories.base_repository import BaseRepository


class StudyRepository(BaseRepository[Study]):
    """Repository for Study persistence operations."""

    def __init__(self, session) -> None:
        super().__init__(session, Study)
