from __future__ import annotations

from models.customer import Customer
from repositories.customer_repository import CustomerRepository
from services.base_service import BaseService


class CustomerService(BaseService[Customer]):
    """Service for managing customer records."""

    def __init__(self, repository: CustomerRepository) -> None:
        super().__init__(repository)

    def create_customer(self, *, name: str, customer_code: str, contact_email: str | None = None) -> Customer:
        if not name or not name.strip():
            raise ValueError("name is required")
        if not customer_code or not customer_code.strip():
            raise ValueError("customer_code is required")

        customer = Customer(
            name=name.strip(),
            customer_code=customer_code.strip(),
            contact_email=contact_email.strip() if contact_email else None,
        )
        return self.create(customer)
