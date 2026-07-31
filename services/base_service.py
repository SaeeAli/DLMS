from __future__ import annotations

from typing import Generic, TypeVar

from repositories.base_repository import BaseRepository

T = TypeVar("T")


class BaseService(Generic[T]):
    """Base service with repository dependency injection for domain operations."""

    def __init__(self, repository: BaseRepository[T]) -> None:
        self.repository = repository

    def create(self, instance: T) -> T:
        return self.repository.create(instance)

    def update(self, instance: T) -> T:
        return self.repository.update(instance)

    def delete(self, instance: T) -> None:
        self.repository.delete(instance)

    def get_by_id(self, instance_id: str) -> T | None:
        return self.repository.get_by_id(instance_id)

    def get_all(self) -> list[T]:
        return self.repository.get_all()

    def exists(self, instance_id: str) -> bool:
        return self.repository.exists(instance_id)
