"""Application configuration backed by environment variables.

Settings are loaded once at import time via :func:`get_settings`, which is
cached so the same immutable :class:`Settings` instance is shared across the
process. Values may be overridden through environment variables prefixed with
``FEATURE_STORE_`` or via a local ``.env`` file.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the feature store service."""

    model_config = SettingsConfigDict(
        env_prefix="FEATURE_STORE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Service metadata
    app_name: str = Field(default="feature-store-platform")
    environment: str = Field(default="development")
    log_level: str = Field(default="INFO")

    # HTTP server
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)

    # Online store (Redis)
    redis_url: str = Field(default="redis://localhost:6379/0")
    redis_key_prefix: str = Field(default="fs")
    online_ttl_seconds: int = Field(default=86_400)

    # Offline store (object storage / warehouse)
    offline_store_uri: str = Field(default="file:///var/lib/feature-store/offline")
    offline_store_format: str = Field(default="parquet")

    # Registry
    registry_path: str = Field(default="file:///var/lib/feature-store/registry.db")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached, process-wide :class:`Settings` instance."""

    return Settings()
