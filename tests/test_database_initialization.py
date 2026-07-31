from sqlalchemy import inspect

from database.base import Base
from database.engine import get_engine
from database.initialization import initialize_database


def test_database_initialization_creates_expected_tables() -> None:
    engine = get_engine()
    initialize_database()

    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    for table_name in Base.metadata.tables:
        assert table_name in existing_tables
