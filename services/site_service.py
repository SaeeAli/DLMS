from __future__ import annotations

from models.site import Site
from repositories.site_repository import SiteRepository
from services.base_service import BaseService


class SiteService(BaseService[Site]):
    """Service for managing site records."""

    def __init__(self, repository: SiteRepository) -> None:
        super().__init__(repository)

    def create_site(self, *, name: str, site_code: str, customer_id: str) -> Site:
        if not name or not name.strip():
            raise ValueError("name is required")
        if not site_code or not site_code.strip():
            raise ValueError("site_code is required")
        if not customer_id or not customer_id.strip():
            raise ValueError("customer_id is required")

        site = Site(name=name.strip(), site_code=site_code.strip(), customer_id=customer_id.strip())
        return self.create(site)
