from __future__ import annotations

import os
from pathlib import Path

from config.constants import DATA_DIR_NAME, DEFAULT_DATABASE_FILENAME, LOGS_DIR_NAME, RESOURCES_DIR_NAME


def get_application_root() -> Path:
    """Return the application root directory using the current file location."""
    return Path(__file__).resolve().parent.parent


APP_ROOT = get_application_root()
DATA_DIR = APP_ROOT / DATA_DIR_NAME
LOGS_DIR = APP_ROOT / LOGS_DIR_NAME
RESOURCES_DIR = APP_ROOT / RESOURCES_DIR_NAME
DATABASE_PATH = DATA_DIR / DEFAULT_DATABASE_FILENAME


def ensure_directories() -> None:
    """Create application data directories if they do not exist."""
    for directory in (DATA_DIR, LOGS_DIR, RESOURCES_DIR):
        directory.mkdir(parents=True, exist_ok=True)


ensure_directories()
