from __future__ import annotations

from models.supplier import Supplier
from repositories.base_repository import BaseRepository


class SupplierRepository(BaseRepository[Supplier]):
    """Repository for Supplier persistence operations."""

    def __init__(self, session) -> None:
        super().__init__(session, Supplier)
