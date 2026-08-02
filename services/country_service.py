from __future__ import annotations

from models.country import Country
from models.customer import Customer
from models.site import Site
from models.study import Study
from models.study_country import StudyCountry
from repositories.country_repository import CountryRepository
from repositories.site_repository import SiteRepository
from repositories.study_country_repository import StudyCountryRepository
from repositories.study_repository import StudyRepository
from services.base_service import BaseService


class CountryService(BaseService[StudyCountry]):
    """Service for managing country and site records in a unified workflow."""

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

    def get_country_records(self) -> list[Site]:
        return self.site_repository.get_all()

    def get_country_record_by_id(self, site_id: str) -> Site | None:
        return self.site_repository.get_by_id(site_id)

    def create_country_record(
        self,
        *,
        study: Study | None,
        country_name: str,
        site_number: str,
        status: str = "Active",
        notes: str | None = None,
    ) -> Site:
        self._validate_required_fields(study=study, country_name=country_name, site_number=site_number)

        country = self._get_or_create_country(name=country_name)
        assignment = self._get_or_create_assignment(study=study, country=country, status=status, notes=notes)
        self._validate_unique_site_number(assignment=assignment, site_number=site_number, existing_site_id=None)

        site = Site(
            study_country=assignment,
            site_number=site_number.strip(),
            name=site_number.strip(),
            status=status.strip() if status else "Active",
            notes=notes.strip() if notes else None,
        )
        return self.site_repository.create(site)

    def update_country_record(
        self,
        site: Site,
        *,
        study: Study | None,
        country_name: str,
        site_number: str,
        status: str = "Active",
        notes: str | None = None,
    ) -> Site:
        if site.id is None:
            raise ValueError("site id is required")

        self._validate_required_fields(study=study, country_name=country_name, site_number=site_number)

        country = self._get_or_create_country(name=country_name)
        assignment = self._get_or_create_assignment(study=study, country=country, status=status, notes=notes)
        self._validate_unique_site_number(assignment=assignment, site_number=site_number, existing_site_id=site.id)

        site.study_country = assignment
        site.site_number = site_number.strip()
        site.name = site_number.strip()
        site.status = status.strip() if status else "Active"
        site.notes = notes.strip() if notes else None
        self.site_repository.update(site)

        assignment.status = status.strip() if status else "Active"
        assignment.notes = notes.strip() if notes else None
        self.update(assignment)
        return site

    def delete_country_record(self, site: Site) -> None:
        if site.id is None:
            raise ValueError("site id is required")

        assignment = site.study_country
        self.site_repository.delete(site)
        if assignment is not None and assignment.id is not None:
            remaining_sites = [existing for existing in self.site_repository.get_all() if existing.study_country_id == assignment.id]
            if not remaining_sites:
                self.delete(assignment)

    def search_countries(self, query: str) -> list[Site]:
        if not query:
            return self.get_country_records()

        normalized = query.strip().lower()
        return [
            site
            for site in self.get_country_records()
            if normalized in (site.study_country.study.study_number or "").lower()
            or normalized in (site.study_country.country.name or "").lower()
            or normalized in (site.site_number or "").lower()
            or normalized in (site.status or "").lower()
        ]

    def get_study_options(self) -> list[Study]:
        return self.study_repository.get_all()

    def get_customer_options(self) -> list[Customer]:
        customers = []
        seen_ids: set[str] = set()
        for study in self.get_study_options():
            customer = study.customer
            if customer is None or customer.id is None:
                continue
            if customer.id in seen_ids:
                continue
            seen_ids.add(customer.id)
            customers.append(customer)
        return customers

    def _validate_required_fields(self, *, study: Study | None, country_name: str, site_number: str) -> None:
        if study is None:
            raise ValueError("study is required")
        if not country_name or not country_name.strip():
            raise ValueError("country name is required")
        if not site_number or not site_number.strip():
            raise ValueError("site_number is required")

    def _validate_unique_site_number(self, *, assignment: StudyCountry, site_number: str, existing_site_id: str | None) -> None:
        normalized = site_number.strip().lower()
        for existing in self.site_repository.get_all():
            if existing.id == existing_site_id:
                continue
            if existing.study_country_id != assignment.id:
                continue
            if (existing.site_number or "").strip().lower() == normalized:
                raise ValueError("A site with this site number already exists for this study country")

    def _get_or_create_assignment(self, *, study: Study | None, country: Country, status: str, notes: str | None) -> StudyCountry:
        if study is None:
            raise ValueError("study is required")

        for existing in self.get_all():
            if existing.study_id == study.id and existing.country_id == country.id:
                existing.status = status.strip() if status else "Active"
                existing.notes = notes.strip() if notes else None
                return self.update(existing)

        assignment = StudyCountry(
            study=study,
            country=country,
            status=status.strip() if status else "Active",
            notes=notes.strip() if notes else None,
        )
        return self.create(assignment)

    def _get_or_create_country(self, *, name: str) -> Country:
        normalized_name = name.strip().lower()
        for existing in self.country_repository.get_all():
            if (existing.name or "").strip().lower() == normalized_name:
                return existing

        country = Country(name=name.strip())
        return self.country_repository.create(country)
