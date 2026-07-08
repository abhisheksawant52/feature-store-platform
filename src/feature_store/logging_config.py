"""Structured logging configuration.

Provides :func:`configure_logging`, which installs a single stream handler with
a consistent, machine-parseable format. Call it once during application
startup before any other module emits log records.
"""

from __future__ import annotations

import logging
from typing import Optional

_LOG_FORMAT = "%(asctime)s %(levelname)-8s %(name)s %(message)s"
_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"


def configure_logging(level: str = "INFO") -> None:
    """Configure the root logger for the service.

    Args:
        level: The minimum log level name (e.g. ``"INFO"``, ``"DEBUG"``).
    """

    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format=_LOG_FORMAT,
        datefmt=_DATE_FORMAT,
    )
    # Align common third-party loggers with our configured level.
    for noisy in ("uvicorn.access", "uvicorn.error"):
        logging.getLogger(noisy).setLevel(numeric_level)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Return a named logger, defaulting to the package root logger."""

    return logging.getLogger(name or "feature_store")
