from __future__ import annotations

from models.customer import Customer
from repositories.customer_repository import CustomerRepository
from services.base_service import BaseService


class CustomerService(BaseService[Customer]):
    """Service for managing customer records."""

    def __init__(self, repository: CustomerRepository) -> None:
        super().__init__(repository)

    def create_customer(self, *, name: str, contact_email: str | None = None) -> Customer:
        self._validate_required_fields(name=name)

        customer = Customer(
            name=name.strip(),
            contact_email=contact_email.strip() if contact_email else None,
        )
        return self.create(customer)

    def update_customer(self, customer: Customer, *, name: str, contact_email: str | None = None) -> Customer:
        if customer.id is None:
            raise ValueError("customer id is required")

        self._validate_required_fields(name=name)

        customer.name = name.strip()
        customer.contact_email = contact_email.strip() if contact_email else None
        return self.update(customer)

    def delete_customer(self, customer: Customer) -> None:
        if customer.id is None:
            raise ValueError("customer id is required")
        self.delete(customer)

    def search_customers(self, query: str) -> list[Customer]:
        if not query:
            return self.get_all()

        normalized = query.strip().lower()
        return [
            customer
            for customer in self.get_all()
            if normalized in customer.name.lower()
            or normalized in (customer.contact_email or "").lower()
        ]

    def _validate_required_fields(self, *, name: str) -> None:
        if not name or not name.strip():
            raise ValueError("name is required")
