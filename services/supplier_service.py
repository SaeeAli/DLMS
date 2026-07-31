from __future__ import annotations

from models.supplier import Supplier
from repositories.supplier_repository import SupplierRepository
from services.base_service import BaseService


class SupplierService(BaseService[Supplier]):
    """Service for managing supplier records."""

    def __init__(self, repository: SupplierRepository) -> None:
        super().__init__(repository)

    def create_supplier(self, *, name: str, supplier_code: str, contact_email: str | None = None) -> Supplier:
        if not name or not name.strip():
            raise ValueError("name is required")
        if not supplier_code or not supplier_code.strip():
            raise ValueError("supplier_code is required")

        supplier = Supplier(
            name=name.strip(),
            supplier_code=supplier_code.strip(),
            contact_email=contact_email.strip() if contact_email else None,
        )
        return self.create(supplier)
