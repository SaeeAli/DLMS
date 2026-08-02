from __future__ import annotations

from models.site import Site
from models.study_country import StudyCountry
from repositories.site_repository import SiteRepository
from repositories.study_country_repository import StudyCountryRepository
from services.base_service import BaseService


class SiteService(BaseService[Site]):
    """Service for managing study-country scoped site records."""

    def __init__(self, repository: SiteRepository, study_country_repository: StudyCountryRepository) -> None:
        super().__init__(repository)
        self.study_country_repository = study_country_repository

    def create_site(
        self,
        *,
        study_country: StudyCountry | None,
        site_number: str,
        name: str,
        address: str | None = None,
        city: str | None = None,
        status: str = "Active",
        notes: str | None = None,
    ) -> Site:
        self._validate_required_fields(study_country=study_country, site_number=site_number, name=name)
        self._validate_unique_site_number(study_country=study_country, site_number=site_number, existing_id=None)

        site = Site(
            study_country=study_country,
            site_number=site_number.strip(),
            name=name.strip(),
            address=address.strip() if address else None,
            city=city.strip() if city else None,
            status=status.strip() if status else "Active",
            notes=notes.strip() if notes else None,
        )
        return self.create(site)

    def update_site(
        self,
        site: Site,
        *,
        study_country: StudyCountry | None,
        site_number: str,
        name: str,
        address: str | None = None,
        city: str | None = None,
        status: str = "Active",
        notes: str | None = None,
    ) -> Site:
        if site.id is None:
            raise ValueError("site id is required")

        self._validate_required_fields(study_country=study_country, site_number=site_number, name=name)
        self._validate_unique_site_number(study_country=study_country, site_number=site_number, existing_id=site.id)

        site.study_country = study_country
        site.site_number = site_number.strip()
        site.name = name.strip()
        site.address = address.strip() if address else None
        site.city = city.strip() if city else None
        site.status = status.strip() if status else "Active"
        site.notes = notes.strip() if notes else None
        return self.update(site)

    def delete_site(self, site: Site) -> None:
        if site.id is None:
            raise ValueError("site id is required")
        self.delete(site)

    def search_sites(self, query: str) -> list[Site]:
        if not query:
            return self.get_all()

        normalized = query.strip().lower()
        return [
            site
            for site in self.get_all()
            if normalized in (site.study_country.study.customer.name or "").lower()
            or normalized in (site.study_country.study.study_number or "").lower()
            or normalized in (site.study_country.country.name or "").lower()
            or normalized in (site.site_number or "").lower()
            or normalized in (site.name or "").lower()
            or normalized in (site.status or "").lower()
        ]

    def get_study_country_options(self) -> list[StudyCountry]:
        return self.study_country_repository.get_all()

    def _validate_required_fields(
        self,
        *,
        study_country: StudyCountry | None,
        site_number: str,
        name: str,
    ) -> None:
        if study_country is None:
            raise ValueError("study_country is required")
        if not site_number or not site_number.strip():
            raise ValueError("site_number is required")
        if not name or not name.strip():
            raise ValueError("name is required")

    def _validate_unique_site_number(
        self,
        *,
        study_country: StudyCountry | None,
        site_number: str,
        existing_id: str | None,
    ) -> None:
        if study_country is None:
            return

        normalized = site_number.strip().lower()
        for existing in self.get_all():
            if existing.id == existing_id:
                continue
            if existing.study_country_id != study_country.id:
                continue
            if (existing.site_number or "").strip().lower() == normalized:
                raise ValueError("A site with this site number already exists for this study country")
