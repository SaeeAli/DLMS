from __future__ import annotations

from models.country import Country
from models.study import Study
from models.study_country import StudyCountry
from repositories.country_repository import CountryRepository
from repositories.site_repository import SiteRepository
from repositories.study_country_repository import StudyCountryRepository
from repositories.study_repository import StudyRepository
from services.base_service import BaseService


class CountryService(BaseService[StudyCountry]):
    """Service for managing country assignments within studies."""

    def __init__(
        self,
        repository: StudyCountryRepository,
        country_repository: CountryRepository,
        study_repository: StudyRepository,
        site_repository: SiteRepository,
    ) -> None:
        super().__init__(repository)
        self.country_repository = country_repository
        self.study_repository = study_repository
        self.site_repository = site_repository

    def create_country(
        self,
        *,
        study: Study | None,
        name: str,
        country_code: str | None = None,
        status: str = "Active",
        notes: str | None = None,
    ) -> StudyCountry:
        self._validate_required_fields(study=study, name=name)

        country = self._get_or_create_country(name=name, country_code=country_code)
        self._validate_unique_country(study=study, country=country, existing_id=None)

        assignment = StudyCountry(
            study=study,
            country=country,
            status=status.strip() if status else "Active",
            notes=notes.strip() if notes else None,
        )
        return self.create(assignment)

    def update_country(
        self,
        assignment: StudyCountry,
        *,
        study: Study | None,
        name: str,
        country_code: str | None = None,
        status: str = "Active",
        notes: str | None = None,
    ) -> StudyCountry:
        if assignment.id is None:
            raise ValueError("country assignment id is required")

        self._validate_required_fields(study=study, name=name)
        country = self._get_or_create_country(name=name, country_code=country_code)
        self._validate_unique_country(study=study, country=country, existing_id=assignment.id)

        assignment.study = study
        assignment.country = country
        assignment.status = status.strip() if status else "Active"
        assignment.notes = notes.strip() if notes else None
        return self.update(assignment)

    def delete_country(self, assignment: StudyCountry) -> None:
        if assignment.id is None:
            raise ValueError("country assignment id is required")
        if assignment.sites:
            raise ValueError("Cannot delete a country assignment that has sites")
        self.delete(assignment)

    def search_countries(self, query: str) -> list[StudyCountry]:
        if not query:
            return self.get_all()

        normalized = query.strip().lower()
        return [
            assignment
            for assignment in self.get_all()
            if normalized in (assignment.study.study_number or "").lower()
            or normalized in (assignment.study.customer.name or "").lower()
            or normalized in (assignment.country.name or "").lower()
            or normalized in (assignment.country.country_code or "").lower()
            or normalized in (assignment.status or "").lower()
        ]

    def get_study_options(self) -> list[Study]:
        return self.study_repository.get_all()

    def _validate_required_fields(self, *, study: Study | None, name: str) -> None:
        if study is None:
            raise ValueError("study is required")
        if not name or not name.strip():
            raise ValueError("country name is required")

    def _validate_unique_country(self, *, study: Study | None, country: Country, existing_id: str | None) -> None:
        if study is None:
            return

        for existing in self.get_all():
            if existing.id == existing_id:
                continue
            if existing.study_id == study.id and existing.country_id == country.id:
                raise ValueError("A country with this name already exists for this study")

    def _get_or_create_country(self, *, name: str, country_code: str | None) -> Country:
        normalized_name = name.strip().lower()
        for existing in self.country_repository.get_all():
            if (existing.name or "").strip().lower() == normalized_name:
                if country_code and not existing.country_code:
                    existing.country_code = country_code.strip()
                    self.country_repository.update(existing)
                return existing

        country = Country(
            name=name.strip(),
            country_code=country_code.strip() if country_code else None,
        )
        return self.country_repository.create(country)
