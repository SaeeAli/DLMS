from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from config.constants import (
    APP_NAME,
    APP_VERSION,
    DATABASE_URL_VARIABLE,
    DEBUG_VARIABLE,
    DEFAULT_ENVIRONMENT,
    ENVIRONMENT_VARIABLE,
    SQLALCHEMY_ECHO_VARIABLE,
)
from config.paths import APP_ROOT, DATABASE_PATH, ensure_directories


@dataclass(frozen=True)
class AppSettings:
    """Application configuration container with environment-aware defaults."""

    app_name: str = APP_NAME
    app_version: str = APP_VERSION
    environment: str = os.getenv(ENVIRONMENT_VARIABLE, DEFAULT_ENVIRONMENT)
    debug: bool = os.getenv(DEBUG_VARIABLE, "0") == "1"
    database_url: str = os.getenv(
        DATABASE_URL_VARIABLE,
        f"sqlite:///{DATABASE_PATH.resolve().as_posix()}",
    )
    sqlalchemy_echo: bool = os.getenv(SQLALCHEMY_ECHO_VARIABLE, "0") == "1"
    app_root: Path = APP_ROOT


settings = AppSettings()
ensure_directories()


def get_settings() -> AppSettings:
    """Return the shared application settings instance."""
    return settings
