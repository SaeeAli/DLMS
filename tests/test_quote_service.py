from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from database.base import Base
from models.country import Country
from models.customer import Customer
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
from services.quote_service import QuoteService


def _make_service(session: Session) -> QuoteService:
    return QuoteService(
        QuoteRepository(session),
        CustomerRepository(session),
        StudyRepository(session),
        StudyCountryRepository(session),
        SiteRepository(session),
        CountryRepository(session),
    )


def _seed_sites(session: Session) -> tuple[Site, Site, Site]:
    customer = Customer(name="Acme")
    study = Study(study_number="ST-100", customer=customer)
    country = Country(name="Germany")
    country_two = Country(name="France")
    assignment = StudyCountry(study=study, country=country)
    assignment_two = StudyCountry(study=study, country=country_two)
    site = Site(name="Berlin Site", site_number="S-001", study_country=assignment)
    site_two = Site(name="Munich Site", site_number="S-002", study_country=assignment)
    site_three = Site(name="Paris Site", site_number="S-003", study_country=assignment_two)
    session.add_all([customer, study, country, country_two, assignment, assignment_two, site, site_two, site_three])
    session.flush()
    return site, site_two, site_three


def test_quote_service_create_and_search_quote() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        service = _make_service(session)
        site, site_two, _ = _seed_sites(session)

        created = service.create_quote(
            quote_number="Q-001",
            sites=[site, site_two],
            quote_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
            status="Draft",
            notes="Initial quote",
        )

        assert created.id is not None
        assert len(created.quote_sites) == 2
        results = service.search_quotes("q-001")
        assert len(results) == 1
        assert results[0].id == created.id
        assert len(service.search_quotes("s-002")) == 1


def test_quote_service_validates_uniqueness_and_required_fields() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        service = _make_service(session)
        site, site_two, site_other_country = _seed_sites(session)

        service.create_quote(
            quote_number="Q-001",
            sites=[site],
            quote_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
            status="Draft",
        )

        with pytest.raises(ValueError, match="already exists"):
            service.create_quote(
                quote_number="Q-001",
                sites=[site],
                quote_date=datetime(2026, 1, 2, tzinfo=timezone.utc),
                status="Sent",
            )

        with pytest.raises(ValueError, match="at least one site is required"):
            service.create_quote(
                quote_number="Q-002",
                sites=[],
                quote_date=datetime(2026, 1, 2, tzinfo=timezone.utc),
                status="Draft",
            )

        with pytest.raises(ValueError, match="quote_date is required"):
            service.create_quote(
                quote_number="Q-003",
                sites=[site],
                quote_date=None,
                status="Draft",
            )

        with pytest.raises(ValueError, match="same study and country"):
            service.create_quote(
                quote_number="Q-004",
                sites=[site_two, site_other_country],
                quote_date=datetime(2026, 1, 2, tzinfo=timezone.utc),
                status="Draft",
            )


def test_quote_service_delete_quote_cascades_quote_sites() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        service = _make_service(session)
        site, site_two, _ = _seed_sites(session)

        created = service.create_quote(
            quote_number="Q-900",
            sites=[site, site_two],
            quote_date=datetime(2026, 2, 1, tzinfo=timezone.utc),
            status="Draft",
        )
        quote_site_ids = [quote_site.id for quote_site in created.quote_sites]
        assert all(quote_site_id is not None for quote_site_id in quote_site_ids)

        service.delete_quote(created)
        session.flush()

        assert service.get_by_id(created.id) is None
        remaining = session.query(QuoteSite).all()
        assert len(remaining) == 0
