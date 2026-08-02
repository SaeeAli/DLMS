from __future__ import annotations

from models.study_country import StudyCountry
from repositories.base_repository import BaseRepository


class StudyCountryRepository(BaseRepository[StudyCountry]):
    """Repository for StudyCountry persistence operations."""

    def __init__(self, session) -> None:
        super().__init__(session, StudyCountry)
