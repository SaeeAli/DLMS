from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from database.base import Base
from models.country import Country
from models.customer import Customer
from models.quote import Quote
from models.site import Site
from models.study import Study
from models.study_country import StudyCountry
from repositories.quote_repository import QuoteRepository


def test_quote_repository_persists_quote() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        customer = Customer(name="Acme")
        study = Study(study_number="ST-100", customer=customer)
        country = Country(name="Germany")
        assignment = StudyCountry(study=study, country=country)
        site = Site(name="Berlin Site", site_number="S-001", study_country=assignment)

        repository = QuoteRepository(session)
        quote = Quote(
            quote_number="Q-100",
            site=site,
            quote_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
            status="Draft",
            notes="Initial quote",
        )
        created = repository.create(quote)

        assert created.id is not None
        assert repository.get_by_id(created.id) is not None
