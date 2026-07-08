"""FastAPI application entrypoint for the feature store serving API.

Creates the app via :func:`create_app`, wiring in the health probes and the
feature serving routes. Run locally with::

    uvicorn feature_store.main:app --reload
"""

from __future__ import annotations

from fastapi import FastAPI

from . import __version__
from .api import features, health
from .config import get_settings
from .logging_config import configure_logging, get_logger


def create_app() -> FastAPI:
    """Build and configure the FastAPI application instance."""

    settings = get_settings()
    configure_logging(settings.log_level)
    logger = get_logger(__name__)

    app = FastAPI(
        title="Feature Store Platform",
        version=__version__,
        summary="Offline and online feature storage, materialization, and serving.",
    )

    app.include_router(health.router)
    app.include_router(features.router)

    logger.info(
        "Feature store API initialized (env=%s, version=%s)",
        settings.environment,
        __version__,
    )
    return app


app = create_app()
