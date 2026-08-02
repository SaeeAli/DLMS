from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from database.base import Base
from models.country import Country
from models.customer import Customer
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


def _seed_site(session: Session) -> Site:
    customer = Customer(name="Acme")
    study = Study(study_number="ST-100", customer=customer)
    country = Country(name="Germany")
    assignment = StudyCountry(study=study, country=country)
    site = Site(name="Berlin Site", site_number="S-001", study_country=assignment)
    session.add_all([customer, study, country, assignment, site])
    session.flush()
    return site


def test_quote_service_create_and_search_quote() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        service = _make_service(session)
        site = _seed_site(session)

        created = service.create_quote(
            quote_number="Q-001",
            site=site,
            quote_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
            status="Draft",
            notes="Initial quote",
        )

        assert created.id is not None
        results = service.search_quotes("q-001")
        assert len(results) == 1
        assert results[0].id == created.id


def test_quote_service_validates_uniqueness_and_required_fields() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        service = _make_service(session)
        site = _seed_site(session)

        service.create_quote(
            quote_number="Q-001",
            site=site,
            quote_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
            status="Draft",
        )

        with pytest.raises(ValueError, match="already exists"):
            service.create_quote(
                quote_number="Q-001",
                site=site,
                quote_date=datetime(2026, 1, 2, tzinfo=timezone.utc),
                status="Sent",
            )

        with pytest.raises(ValueError, match="site is required"):
            service.create_quote(
                quote_number="Q-002",
                site=None,
                quote_date=datetime(2026, 1, 2, tzinfo=timezone.utc),
                status="Draft",
            )

        with pytest.raises(ValueError, match="quote_date is required"):
            service.create_quote(
                quote_number="Q-003",
                site=site,
                quote_date=None,
                status="Draft",
            )
