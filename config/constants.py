from __future__ import annotations

from pathlib import Path

APP_NAME = "DLMS"
APP_VERSION = "0.1.0"
DEFAULT_ENVIRONMENT = "development"

# File and directory names
DATA_DIR_NAME = "data"
LOGS_DIR_NAME = "logs"
RESOURCES_DIR_NAME = "resources"

# Default database file
DEFAULT_DATABASE_FILENAME = "dlms.sqlite3"

# Environment variable names
ENVIRONMENT_VARIABLE = "DLMS_ENV"
DATABASE_URL_VARIABLE = "DLMS_DATABASE_URL"
SQLALCHEMY_ECHO_VARIABLE = "DLMS_SQLALCHEMY_ECHO"
DEBUG_VARIABLE = "DLMS_DEBUG"
