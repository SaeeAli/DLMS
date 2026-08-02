from __future__ import annotations

from models.customer import Customer
from models.study import Study
from repositories.customer_repository import CustomerRepository
from repositories.study_repository import StudyRepository
from services.base_service import BaseService


class StudyService(BaseService[Study]):
    """Service for managing study records."""

    def __init__(self, repository: StudyRepository, customer_repository: CustomerRepository) -> None:
        super().__init__(repository)
        self.customer_repository = customer_repository

    def create_study(
        self,
        *,
        customer: Customer,
        study_number: str,
        study_name: str | None = None,
        status: str = "Active",
        notes: str | None = None,
    ) -> Study:
        self._validate_required_fields(customer=customer, study_number=study_number)
        self._validate_unique_study_number(customer=customer, study_number=study_number, existing_id=None)

        study = Study(
            customer=customer,
            study_number=study_number.strip(),
            study_name=study_name.strip() if study_name else None,
            status=status.strip() if status else "Active",
            notes=notes.strip() if notes else None,
        )
        return self.create(study)

    def update_study(
        self,
        study: Study,
        *,
        customer: Customer,
        study_number: str,
        study_name: str | None = None,
        status: str = "Active",
        notes: str | None = None,
    ) -> Study:
        if study.id is None:
            raise ValueError("study id is required")

        self._validate_required_fields(customer=customer, study_number=study_number)
        self._validate_unique_study_number(customer=customer, study_number=study_number, existing_id=study.id)

        study.customer = customer
        study.study_number = study_number.strip()
        study.study_name = study_name.strip() if study_name else None
        study.status = status.strip() if status else "Active"
        study.notes = notes.strip() if notes else None
        return self.update(study)

    def delete_study(self, study: Study) -> None:
        if study.id is None:
            raise ValueError("study id is required")

        self.delete(study)

    def search_studies(self, query: str) -> list[Study]:
        if not query:
            return self.get_all()

        normalized = query.strip().lower()
        return [
            study
            for study in self.get_all()
            if normalized in (study.customer.name or "").lower()
            or normalized in (study.study_number or "").lower()
            or normalized in (study.study_name or "").lower()
            or normalized in (study.status or "").lower()
        ]

    def get_customer_options(self) -> list[Customer]:
        return self.customer_repository.get_all()

    def _validate_required_fields(self, *, customer: Customer, study_number: str) -> None:
        if customer is None:
            raise ValueError("customer is required")
        if not study_number or not study_number.strip():
            raise ValueError("study_number is required")

    def _validate_unique_study_number(self, *, customer: Customer, study_number: str, existing_id: str | None) -> None:
        normalized = study_number.strip().lower()
        for existing in self.get_all():
            if existing.id == existing_id:
                continue
            if existing.customer_id != customer.id:
                continue
            if (existing.study_number or "").strip().lower() == normalized:
                raise ValueError("A study with this study number already exists for this customer")
