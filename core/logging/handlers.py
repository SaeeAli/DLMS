from __future__ import annotations

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional

from config.paths import LOGS_DIR, ensure_directories


DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_LOG_FILE = LOGS_DIR / "dlms.log"


def _build_rotating_file_handler(log_file: Path, level: int = logging.INFO) -> logging.Handler:
    """Create a rotating file handler for persistent application logs."""
    log_file.parent.mkdir(parents=True, exist_ok=True)
    handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT))
    return handler


def _build_console_handler(level: int = logging.INFO) -> logging.Handler:
    """Create a console handler for local development output."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT))
    return handler


def configure_logging(level: int = logging.INFO, log_file: Optional[Path] = None) -> logging.Logger:
    """Configure application-wide logging with console and rotating file handlers."""
    ensure_directories()
    log_path = log_file or DEFAULT_LOG_FILE
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("dlms")
    logger.setLevel(level)
    logger.handlers.clear()

    file_handler = _build_rotating_file_handler(log_path, level=logging.INFO)
    console_handler = _build_console_handler(level=logging.INFO)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.propagate = False

    return logger


def get_logger(name: str) -> logging.Logger:
    """Return a named logger that inherits the application logging configuration."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        root_logger = logging.getLogger("dlms")
        if root_logger.handlers:
            logger.handlers = list(root_logger.handlers)
            logger.setLevel(root_logger.level)
            logger.propagate = False
    return logger
