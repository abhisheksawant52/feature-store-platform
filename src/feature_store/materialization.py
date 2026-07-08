"""Materialization jobs: move features from the offline store to the online store.

Materialization reads the latest value per entity from the offline store for a
given feature view and writes it into the online store so it can be served with
low latency. In production this runs on a schedule (e.g. an hourly batch job or
a streaming sink); here it is expressed as a synchronous, testable function.
"""

from __future__ import annotations

from dataclasses import dataclass

from .logging_config import get_logger
from .offline_store import OfflineStore
from .online_store import OnlineStore
from .registry import FeatureView

logger = get_logger(__name__)


@dataclass(frozen=True)
class MaterializationResult:
    """Summary of a materialization run.

    Attributes:
        feature_view: The name of the materialized feature view.
        rows_written: Number of entity rows pushed to the online store.
    """

    feature_view: str
    rows_written: int


class Materializer:
    """Coordinates offline-to-online materialization for feature views."""

    def __init__(self, offline: OfflineStore, online: OnlineStore) -> None:
        self._offline = offline
        self._online = online

    def materialize(self, feature_view: FeatureView) -> MaterializationResult:
        """Materialize the latest values of a feature view into the online store.

        Args:
            feature_view: The feature view to materialize.

        Returns:
            A :class:`MaterializationResult` describing what was written.
        """

        latest = self._offline.get_latest(feature_view)
        feature_cols = [f.name for f in feature_view.features]
        entity_cols = list(feature_view.entities)
        ttl_seconds = int(feature_view.ttl.total_seconds())

        rows_written = 0
        for record in latest.to_dict(orient="records"):
            entity_key = ":".join(str(record[col]) for col in entity_cols)
            values = {col: record[col] for col in feature_cols if col in record}
            self._online.write(feature_view.name, entity_key, values, ttl_seconds)
            rows_written += 1

        logger.info(
            "Materialized %d rows for feature view '%s'",
            rows_written,
            feature_view.name,
        )
        return MaterializationResult(feature_view=feature_view.name, rows_written=rows_written)
