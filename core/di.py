from __future__ import annotations

from typing import Any, Callable, Dict


class ServiceContainer:
    """Minimal dependency injection container for future service registration."""

    def __init__(self) -> None:
        self._services: Dict[type, Callable[[], Any]] = {}

    def register(self, service_type: type, factory: Callable[[], Any]) -> None:
        self._services[service_type] = factory

    def resolve(self, service_type: type) -> Any:
        if service_type not in self._services:
            raise KeyError(f"Service {service_type.__name__} is not registered")
        return self._services[service_type]()
