"""Liveness and readiness probe endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from .. import __version__

router = APIRouter(tags=["health"])


@router.get("/health", summary="Liveness probe")
def health() -> dict[str, str]:
    """Return a static liveness response.

    Used by Kubernetes and the container ``HEALTHCHECK`` to confirm the process
    is running and able to serve HTTP.
    """

    return {"status": "ok", "version": __version__}


@router.get("/ready", summary="Readiness probe")
def ready() -> dict[str, str]:
    """Return readiness status.

    A production implementation would verify connectivity to the online store
    here; the endpoint reports ready once the application has started and the
    dependency graph has been constructed.
    """

    return {"status": "ready"}
