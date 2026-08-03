from __future__ import annotations

from datetime import datetime

from models.country import Country
from models.customer import Customer
from models.quote import Quote
from models.quote_site import QuoteSite
from models.site import Site
from models.study import Study
from models.study_country import StudyCountry
from repositories.country_repository import CountryRepository
from repositories.customer_repository import CustomerRepository
from repositories.quote_repository import QuoteRepository
from repositories.site_repository import SiteRepository
from repositories.study_country_repository import StudyCountryRepository
from repositories.study_repository import StudyRepository
from services.base_service import BaseService


class QuoteService(BaseService[Quote]):
    """Service for managing quote records with hierarchical site selection."""

    ALLOWED_STATUSES = {"Draft", "Sent", "Approved", "Rejected", "Expired"}

    def __init__(
        self,
        repository: QuoteRepository,
        customer_repository: CustomerRepository,
        study_repository: StudyRepository,
        study_country_repository: StudyCountryRepository,
        site_repository: SiteRepository,
        country_repository: CountryRepository,
    ) -> None:
        super().__init__(repository)
        self.customer_repository = customer_repository
        self.study_repository = study_repository
        self.study_country_repository = study_country_repository
        self.site_repository = site_repository
        self.country_repository = country_repository

    def create_quote(
        self,
        *,
        quote_number: str,
        sites: list[Site],
        quote_date: datetime | None,
        status: str,
        notes: str | None = None,
    ) -> Quote:
        self._validate_quote_fields(
            quote_number=quote_number,
            sites=sites,
            quote_date=quote_date,
            status=status,
            existing_id=None,
        )

        quote = Quote(
            quote_number=quote_number.strip(),
            quote_date=quote_date,
            status=status.strip(),
            notes=notes.strip() if notes else None,
        )
        quote.quote_sites = [QuoteSite(site=site) for site in sites]
        return self.create(quote)

    def update_quote(
        self,
        quote: Quote,
        *,
        quote_number: str,
        sites: list[Site],
        quote_date: datetime | None,
        status: str,
        notes: str | None = None,
    ) -> Quote:
        if quote.id is None:
            raise ValueError("quote id is required")

        self._validate_quote_fields(
            quote_number=quote_number,
            sites=sites,
            quote_date=quote_date,
            status=status,
            existing_id=quote.id,
        )

        quote.quote_number = quote_number.strip()
        quote.quote_date = quote_date
        quote.status = status.strip()
        quote.notes = notes.strip() if notes else None
        quote.quote_sites = [QuoteSite(site=site) for site in sites]
        return self.update(quote)

    def delete_quote(self, quote: Quote) -> None:
        if quote.id is None:
            raise ValueError("quote id is required")
        self.delete(quote)

    def search_quotes(self, query: str) -> list[Quote]:
        if not query:
            return self.get_all()

        normalized = query.strip().lower()
        return [
            quote
            for quote in self.get_all()
            if normalized in (quote.quote_number or "").lower()
            or normalized in (self._customer_name(quote) or "").lower()
            or normalized in (self._study_number(quote) or "").lower()
            or normalized in (self._country_name(quote) or "").lower()
            or any(normalized in (site_number or "").lower() for site_number in self._site_numbers(quote))
        ]

    def get_customer_options(self) -> list[Customer]:
        return self.customer_repository.get_all()

    def get_study_options(self, customer_id: str | None) -> list[Study]:
        if not customer_id:
            return []
        return [study for study in self.study_repository.get_all() if study.customer_id == customer_id]

    def get_country_options(self, study_id: str | None) -> list[Country]:
        if not study_id:
            return []

        countries: list[Country] = []
        for assignment in self._study_country_options(study_id=study_id):
            if assignment.country is not None:
                countries.append(assignment.country)
        return countries

    def get_site_options(self, study_id: str | None, country_id: str | None) -> list[Site]:
        if not study_id or not country_id:
            return []

        valid_assignment_ids = {
            assignment.id
            for assignment in self._study_country_options(study_id=study_id)
            if assignment.country_id == country_id and assignment.id is not None
        }
        if not valid_assignment_ids:
            return []

        return [site for site in self.site_repository.get_all() if site.study_country_id in valid_assignment_ids]

    def _study_country_options(self, *, study_id: str) -> list[StudyCountry]:
        return [assignment for assignment in self.study_country_repository.get_all() if assignment.study_id == study_id]

    def _validate_quote_fields(
        self,
        *,
        quote_number: str,
        sites: list[Site],
        quote_date: datetime | None,
        status: str,
        existing_id: str | None,
    ) -> None:
        if not quote_number or not quote_number.strip():
            raise ValueError("quote_number is required")
        if not sites:
            raise ValueError("at least one site is required")
        if quote_date is None:
            raise ValueError("quote_date is required")
        if status.strip() not in self.ALLOWED_STATUSES:
            raise ValueError("status is invalid")

        site_ids = [site.id for site in sites]
        if any(site_id is None for site_id in site_ids):
            raise ValueError("all selected sites must be persisted")
        if len(set(site_ids)) != len(site_ids):
            raise ValueError("selected sites must be unique")

        study_country_ids = {site.study_country_id for site in sites}
        if any(study_country_id is None for study_country_id in study_country_ids):
            raise ValueError("all selected sites must be linked to a study country")
        if len(study_country_ids) != 1:
            raise ValueError("all selected sites must belong to the same study and country")

        normalized = quote_number.strip().lower()
        for existing in self.get_all():
            if existing.id == existing_id:
                continue
            if (existing.quote_number or "").strip().lower() == normalized:
                raise ValueError("A quote with this quote number already exists")

    def _primary_site(self, quote: Quote) -> Site | None:
        if not quote.quote_sites:
            return None
        quote_site = quote.quote_sites[0]
        return quote_site.site

    def _customer_name(self, quote: Quote) -> str:
        site = self._primary_site(quote)
        if site is None or site.study_country is None or site.study_country.study is None or site.study_country.study.customer is None:
            return ""
        return site.study_country.study.customer.name or ""

    def _study_number(self, quote: Quote) -> str:
        site = self._primary_site(quote)
        if site is None or site.study_country is None or site.study_country.study is None:
            return ""
        return site.study_country.study.study_number or ""

    def _country_name(self, quote: Quote) -> str:
        site = self._primary_site(quote)
        if site is None or site.study_country is None or site.study_country.country is None:
            return ""
        return site.study_country.country.name or ""

    def _site_numbers(self, quote: Quote) -> list[str]:
        return [
            quote_site.site.site_number
            for quote_site in quote.quote_sites
            if quote_site.site is not None and quote_site.site.site_number is not None
        ]
