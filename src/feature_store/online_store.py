"""Online store abstraction for low-latency feature lookups.

The online store holds only the *latest* value per entity and is optimized for
single-digit-millisecond reads at serving time. The reference implementation
targets Redis, storing each feature view row as a hash keyed by
``<prefix>:<view>:<entity_key>``.

The Redis client is imported lazily so the module can be imported without the
``redis`` package present (e.g. during static analysis or unit tests that use
the in-memory backend).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, Protocol, runtime_checkable

from .logging_config import get_logger

if TYPE_CHECKING:  # pragma: no cover - typing only
    from redis import Redis

logger = get_logger(__name__)


@runtime_checkable
class OnlineStore(Protocol):
    """Protocol implemented by online store backends."""

    def write(self, view: str, entity_key: str, values: dict[str, Any], ttl: int) -> None:
        """Upsert a single entity's feature values."""
        ...

    def read(self, view: str, entity_key: str, features: list[str]) -> dict[str, Any]:
        """Read the requested feature values for one entity."""
        ...


class RedisOnlineStore:
    """Redis-backed online store.

    Args:
        url: Redis connection URL (``redis://host:port/db``).
        key_prefix: Namespace prefix for all keys written by this store.
    """

    def __init__(self, url: str, key_prefix: str = "fs") -> None:
        self._url = url
        self._key_prefix = key_prefix
        self._client: Optional["Redis"] = None

    @property
    def client(self) -> "Redis":
        """Return a lazily constructed, connection-pooled Redis client."""

        if self._client is None:
            from redis import Redis

            self._client = Redis.from_url(self._url, decode_responses=True)
        return self._client

    def _key(self, view: str, entity_key: str) -> str:
        """Build the namespaced Redis key for a feature view row."""

        return f"{self._key_prefix}:{view}:{entity_key}"

    def write(self, view: str, entity_key: str, values: dict[str, Any], ttl: int) -> None:
        """Upsert an entity's feature hash and set its expiry.

        Args:
            view: Feature view name.
            entity_key: Serialized entity key value.
            values: Mapping of feature name to value.
            ttl: Time-to-live in seconds.
        """

        key = self._key(view, entity_key)
        pipe = self.client.pipeline()
        pipe.hset(key, mapping={k: str(v) for k, v in values.items()})
        if ttl > 0:
            pipe.expire(key, ttl)
        pipe.execute()

    def read(self, view: str, entity_key: str, features: list[str]) -> dict[str, Any]:
        """Read specific feature fields for one entity.

        Returns:
            A mapping of feature name to value; missing features map to ``None``.
        """

        key = self._key(view, entity_key)
        raw = self.client.hmget(key, features)
        return dict(zip(features, raw))


class InMemoryOnlineStore:
    """Dict-backed online store for tests and local development.

    Implements the same :class:`OnlineStore` protocol as
    :class:`RedisOnlineStore` without requiring a running Redis instance. TTLs
    are accepted for API compatibility but not enforced.
    """

    def __init__(self, key_prefix: str = "fs") -> None:
        self._key_prefix = key_prefix
        self._data: dict[str, dict[str, Any]] = {}

    def _key(self, view: str, entity_key: str) -> str:
        return f"{self._key_prefix}:{view}:{entity_key}"

    def write(self, view: str, entity_key: str, values: dict[str, Any], ttl: int) -> None:
        """Store an entity's feature values in memory."""

        self._data.setdefault(self._key(view, entity_key), {}).update(values)

    def read(self, view: str, entity_key: str, features: list[str]) -> dict[str, Any]:
        """Read feature values from the in-memory map."""

        stored = self._data.get(self._key(view, entity_key), {})
        return {name: stored.get(name) for name in features}
