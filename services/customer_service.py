from __future__ import annotations

from models.customer import Customer
from repositories.customer_repository import CustomerRepository
from services.base_service import BaseService


class CustomerService(BaseService[Customer]):
    """Service for managing customer records."""

    def __init__(self, repository: CustomerRepository) -> None:
        super().__init__(repository)

    def create_customer(self, *, name: str, customer_code: str, contact_email: str | None = None) -> Customer:
        self._validate_required_fields(name=name, customer_code=customer_code)
        self._validate_unique_code(customer_code=customer_code, existing_id=None)

        customer = Customer(
            name=name.strip(),
            customer_code=customer_code.strip(),
            contact_email=contact_email.strip() if contact_email else None,
        )
        return self.create(customer)

    def update_customer(self, customer: Customer, *, name: str, customer_code: str, contact_email: str | None = None) -> Customer:
        if customer.id is None:
            raise ValueError("customer id is required")

        self._validate_required_fields(name=name, customer_code=customer_code)
        self._validate_unique_code(customer_code=customer_code, existing_id=customer.id)

        customer.name = name.strip()
        customer.customer_code = customer_code.strip()
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
            or normalized in customer.customer_code.lower()
            or normalized in (customer.contact_email or "").lower()
        ]

    def _validate_required_fields(self, *, name: str, customer_code: str) -> None:
        if not name or not name.strip():
            raise ValueError("name is required")
        if not customer_code or not customer_code.strip():
            raise ValueError("customer_code is required")

    def _validate_unique_code(self, *, customer_code: str, existing_id: str | None) -> None:
        normalized_code = customer_code.strip().lower()
        for existing in self.get_all():
            if existing.id == existing_id:
                continue
            if (existing.customer_code or "").strip().lower() == normalized_code:
                raise ValueError("A customer with this customer code already exists")
