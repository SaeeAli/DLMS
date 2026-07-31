from __future__ import annotations

from models.customer import Customer
from repositories.base_repository import BaseRepository


class CustomerRepository(BaseRepository[Customer]):
    """Repository for Customer persistence operations."""

    def __init__(self, session) -> None:
        super().__init__(session, Customer)
