"""Shared FastAPI dependencies and application-scoped singletons.

These factories build the registry and stores once and expose them to routers
via FastAPI's dependency injection. The online store defaults to the in-memory
backend unless a Redis URL is configured, keeping local development and tests
dependency-free.
"""

from __future__ import annotations

from functools import lru_cache

from ..config import Settings, get_settings
from ..online_store import InMemoryOnlineStore, OnlineStore, RedisOnlineStore
from ..registry import FeatureRegistry, default_registry
from ..serving import FeatureService


@lru_cache(maxsize=1)
def get_registry() -> FeatureRegistry:
    """Return the process-wide feature registry."""

    return default_registry()


def _build_online_store(settings: Settings) -> OnlineStore:
    """Construct the configured online store backend."""

    if settings.redis_url:
        return RedisOnlineStore(url=settings.redis_url, key_prefix=settings.redis_key_prefix)
    return InMemoryOnlineStore(key_prefix=settings.redis_key_prefix)


@lru_cache(maxsize=1)
def get_online_store() -> OnlineStore:
    """Return the process-wide online store."""

    return _build_online_store(get_settings())


def get_feature_service() -> FeatureService:
    """Return a :class:`FeatureService` wired to the registry and online store."""

    return FeatureService(registry=get_registry(), online_store=get_online_store())
