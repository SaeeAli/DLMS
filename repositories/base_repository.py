from __future__ import annotations

from typing import Generic, TypeVar

from sqlalchemy.orm import Session

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Reusable repository with common CRUD operations for SQLAlchemy models."""

    def __init__(self, session: Session, model_type: type[T]) -> None:
        self.session = session
        self.model_type = model_type

    def create(self, instance: T) -> T:
        self.session.add(instance)
        self.session.flush()
        return instance

    def update(self, instance: T) -> T:
        self.session.flush()
        return instance

    def delete(self, instance: T) -> None:
        self.session.delete(instance)
        self.session.flush()

    def get_by_id(self, instance_id: str) -> T | None:
        return self.session.get(self.model_type, instance_id)

    def get_all(self) -> list[T]:
        return list(self.session.query(self.model_type).all())

    def exists(self, instance_id: str) -> bool:
        return self.session.get(self.model_type, instance_id) is not None
