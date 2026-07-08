"""Feature serving logic: online lookups and historical dataset generation.

:class:`FeatureService` ties the registry, offline store, and online store
together behind the two public entry points a feature store exposes:

* :meth:`get_online_features` — low-latency reads for real-time inference, and
* :meth:`get_historical_features` — point-in-time-correct joins for training.
"""

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING, Any

from .logging_config import get_logger
from .offline_store import OfflineStore
from .online_store import OnlineStore
from .registry import FeatureRegistry

if TYPE_CHECKING:  # pragma: no cover - typing only
    import pandas as pd

logger = get_logger(__name__)


class FeatureService:
    """High-level API for retrieving features from the stores."""

    def __init__(
        self,
        registry: FeatureRegistry,
        online_store: OnlineStore,
        offline_store: OfflineStore | None = None,
    ) -> None:
        self._registry = registry
        self._online = online_store
        self._offline = offline_store

    def get_online_features(
        self,
        feature_refs: list[str],
        entity_rows: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Fetch the latest feature values for a set of entities.

        Args:
            feature_refs: References of the form ``"view:feature"``.
            entity_rows: One mapping of entity key names to values per entity.

        Returns:
            One result mapping per input entity row, containing the entity keys
            plus every requested feature.
        """

        # Group requested features by their owning view to minimize lookups.
        by_view: dict[str, list[str]] = defaultdict(list)
        view_objs = {}
        for ref in feature_refs:
            view, feature = self._registry.resolve(ref)
            by_view[view.name].append(feature.name)
            view_objs[view.name] = view

        results: list[dict[str, Any]] = []
        for row in entity_rows:
            record: dict[str, Any] = dict(row)
            for view_name, feature_names in by_view.items():
                view = view_objs[view_name]
                entity_key = ":".join(str(row[e]) for e in view.entities)
                values = self._online.read(view_name, entity_key, feature_names)
                for name in feature_names:
                    record[f"{view_name}:{name}"] = values.get(name)
            results.append(record)

        logger.debug("Served %d online feature rows", len(results))
        return results

    def get_historical_features(
        self,
        entity_df: "pd.DataFrame",
        feature_refs: list[str],
    ) -> "pd.DataFrame":
        """Generate a training dataset via point-in-time-correct joins.

        Args:
            entity_df: Entity keys plus an ``event_timestamp`` column.
            feature_refs: References of the form ``"view:feature"``.

        Returns:
            ``entity_df`` augmented with the requested feature columns.

        Raises:
            RuntimeError: If no offline store is configured.
        """

        if self._offline is None:
            raise RuntimeError("Historical retrieval requires an offline store")

        by_view: dict[str, list[str]] = defaultdict(list)
        for ref in feature_refs:
            view, feature = self._registry.resolve(ref)
            by_view[view.name].append(feature.name)

        result = entity_df
        for view_name, feature_names in by_view.items():
            view = self._registry.get_feature_view(view_name)
            result = self._offline.get_historical_features(result, view, feature_names)
        return result
