"""Feature registry: entities, feature views, and their definitions.

The registry is the source of truth for metadata describing *what* features
exist, their data types, the entities they are keyed by, and where they are
materialized from. Both the offline and online stores resolve schema through
the registry so that reads and writes agree on column names and join keys.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta
from enum import Enum


class ValueType(str, Enum):
    """Supported feature value types."""

    INT64 = "int64"
    FLOAT = "float"
    STRING = "string"
    BOOL = "bool"
    BYTES = "bytes"
    TIMESTAMP = "timestamp"


@dataclass(frozen=True)
class Entity:
    """A domain object features are attached to (e.g. a customer or product).

    Attributes:
        name: Unique entity name, used as the join key column.
        value_type: The physical type of the entity key.
        description: Human-readable description.
    """

    name: str
    value_type: ValueType = ValueType.INT64
    description: str = ""


@dataclass(frozen=True)
class Feature:
    """A single named feature within a feature view."""

    name: str
    value_type: ValueType
    description: str = ""


@dataclass(frozen=True)
class FeatureView:
    """A logical group of features sharing entities and a data source.

    Attributes:
        name: Unique feature view name.
        entities: Names of the entities this view is keyed by.
        features: The features provided by this view.
        ttl: How long a materialized feature value remains fresh online.
        source: URI of the offline source table/path for this view.
    """

    name: str
    entities: tuple[str, ...]
    features: tuple[Feature, ...]
    ttl: timedelta = timedelta(days=1)
    source: str = ""

    def feature_names(self) -> list[str]:
        """Return the fully qualified ``view:feature`` reference strings."""

        return [f"{self.name}:{feature.name}" for feature in self.features]


class FeatureRegistry:
    """In-memory registry of entities and feature views.

    A production deployment would persist this to a backing store (the
    ``registry_path`` setting); this implementation keeps definitions in memory
    with the same lookup semantics for local development and tests.
    """

    def __init__(self) -> None:
        self._entities: dict[str, Entity] = {}
        self._feature_views: dict[str, FeatureView] = {}

    def register_entity(self, entity: Entity) -> None:
        """Register an entity, replacing any existing one with the same name."""

        self._entities[entity.name] = entity

    def register_feature_view(self, view: FeatureView) -> None:
        """Register a feature view.

        Raises:
            KeyError: If the view references an entity that is not registered.
        """

        for entity_name in view.entities:
            if entity_name not in self._entities:
                raise KeyError(f"Unknown entity '{entity_name}' for view '{view.name}'")
        self._feature_views[view.name] = view

    def get_entity(self, name: str) -> Entity:
        """Return a registered entity by name."""

        return self._entities[name]

    def get_feature_view(self, name: str) -> FeatureView:
        """Return a registered feature view by name."""

        return self._feature_views[name]

    def list_feature_views(self) -> list[FeatureView]:
        """Return all registered feature views."""

        return list(self._feature_views.values())

    def resolve(self, reference: str) -> tuple[FeatureView, Feature]:
        """Resolve a ``view:feature`` reference to its definitions.

        Args:
            reference: A reference string of the form ``"view:feature"``.

        Returns:
            A ``(FeatureView, Feature)`` tuple.

        Raises:
            ValueError: If the reference is malformed.
            KeyError: If the view or feature does not exist.
        """

        try:
            view_name, feature_name = reference.split(":", 1)
        except ValueError as exc:  # pragma: no cover - defensive
            raise ValueError(f"Invalid feature reference '{reference}'") from exc

        view = self._feature_views[view_name]
        for feature in view.features:
            if feature.name == feature_name:
                return view, feature
        raise KeyError(f"Feature '{feature_name}' not found in view '{view_name}'")


def default_registry() -> FeatureRegistry:
    """Build a small example registry used for local development and tests."""

    registry = FeatureRegistry()
    registry.register_entity(
        Entity(name="customer_id", value_type=ValueType.INT64, description="Customer key")
    )
    registry.register_feature_view(
        FeatureView(
            name="customer_activity",
            entities=("customer_id",),
            features=(
                Feature("transactions_7d", ValueType.INT64, "Transactions in last 7 days"),
                Feature("avg_basket_value", ValueType.FLOAT, "Average basket value"),
                Feature("is_active", ValueType.BOOL, "Active in last 30 days"),
            ),
            ttl=timedelta(days=1),
            source="s3://feature-store/offline/customer_activity/",
        )
    )
    return registry
