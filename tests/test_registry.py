"""Unit tests for the feature registry and online serving with a fake store."""

from datetime import timedelta

import pytest

from feature_store.online_store import InMemoryOnlineStore
from feature_store.registry import (
    Entity,
    Feature,
    FeatureRegistry,
    FeatureView,
    ValueType,
    default_registry,
)
from feature_store.serving import FeatureService


def test_register_feature_view_requires_known_entity():
    registry = FeatureRegistry()
    view = FeatureView(
        name="orphan",
        entities=("missing_entity",),
        features=(Feature("x", ValueType.INT64),),
    )
    with pytest.raises(KeyError):
        registry.register_feature_view(view)


def test_resolve_returns_view_and_feature():
    registry = default_registry()
    view, feature = registry.resolve("customer_activity:transactions_7d")
    assert view.name == "customer_activity"
    assert feature.name == "transactions_7d"
    assert feature.value_type == ValueType.INT64


def test_feature_view_feature_names():
    view = FeatureView(
        name="v",
        entities=("customer_id",),
        features=(Feature("a", ValueType.INT64), Feature("b", ValueType.FLOAT)),
        ttl=timedelta(hours=6),
    )
    assert view.feature_names() == ["v:a", "v:b"]


def test_online_serving_reads_written_values():
    registry = FeatureRegistry()
    registry.register_entity(Entity(name="customer_id", value_type=ValueType.INT64))
    registry.register_feature_view(
        FeatureView(
            name="customer_activity",
            entities=("customer_id",),
            features=(Feature("transactions_7d", ValueType.INT64),),
        )
    )
    store = InMemoryOnlineStore()
    store.write("customer_activity", "42", {"transactions_7d": 9}, ttl=3600)

    service = FeatureService(registry=registry, online_store=store)
    results = service.get_online_features(
        ["customer_activity:transactions_7d"],
        [{"customer_id": 42}],
    )
    assert results[0]["customer_activity:transactions_7d"] == 9
