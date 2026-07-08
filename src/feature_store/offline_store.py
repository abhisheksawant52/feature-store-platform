"""Offline store abstraction for batch and historical feature retrieval.

The offline store holds the full history of feature values (typically as
partitioned Parquet in object storage or a data warehouse). It supports two
access patterns:

* **historical retrieval** — point-in-time-correct joins used to build training
  datasets, and
* **latest-value scan** — the read side of materialization jobs that push the
  most recent values into the online store.

This module defines a small protocol plus a Parquet-backed reference
implementation. Heavy I/O (pandas / pyarrow) is imported lazily so the module
can be imported cheaply in environments without those dependencies installed.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, Iterable, Protocol, runtime_checkable

from .logging_config import get_logger
from .registry import FeatureView

if TYPE_CHECKING:  # pragma: no cover - typing only
    import pandas as pd

logger = get_logger(__name__)


@runtime_checkable
class OfflineStore(Protocol):
    """Protocol implemented by offline store backends."""

    def get_historical_features(
        self,
        entity_df: "pd.DataFrame",
        feature_view: FeatureView,
        feature_names: Iterable[str],
    ) -> "pd.DataFrame":
        """Return a point-in-time-correct join of features onto ``entity_df``."""
        ...

    def get_latest(self, feature_view: FeatureView) -> "pd.DataFrame":
        """Return the most recent row per entity for ``feature_view``."""
        ...


class ParquetOfflineStore:
    """Offline store backed by Parquet files under a base URI.

    Args:
        base_uri: Root location containing one dataset per feature view.
        event_timestamp_column: Column holding the feature event time.
    """

    def __init__(
        self,
        base_uri: str,
        event_timestamp_column: str = "event_timestamp",
    ) -> None:
        self.base_uri = base_uri.rstrip("/")
        self.event_timestamp_column = event_timestamp_column

    def _dataset_path(self, feature_view: FeatureView) -> str:
        """Return the dataset path for a feature view."""

        return f"{self.base_uri}/{feature_view.name}"

    def _read(self, feature_view: FeatureView) -> "pd.DataFrame":
        """Load the raw dataset for a feature view as a DataFrame."""

        import pandas as pd

        path = self._dataset_path(feature_view)
        logger.debug("Reading offline dataset from %s", path)
        return pd.read_parquet(path)

    def get_historical_features(
        self,
        entity_df: "pd.DataFrame",
        feature_view: FeatureView,
        feature_names: Iterable[str],
    ) -> "pd.DataFrame":
        """Perform a point-in-time-correct join for training data generation.

        For each row in ``entity_df`` (which carries entity keys and an
        ``event_timestamp``), the most recent feature values at or before that
        timestamp are attached.

        Args:
            entity_df: Entity keys plus an ``event_timestamp`` column.
            feature_view: The view providing the requested features.
            feature_names: Bare feature column names to return.

        Returns:
            ``entity_df`` augmented with the requested feature columns.
        """

        import pandas as pd

        source = self._read(feature_view)
        keys = list(feature_view.entities)
        wanted = list(feature_names)

        merged = pd.merge_asof(
            entity_df.sort_values(self.event_timestamp_column),
            source.sort_values(self.event_timestamp_column),
            on=self.event_timestamp_column,
            by=keys,
            direction="backward",
        )
        return merged[[*entity_df.columns, *wanted]]

    def get_latest(self, feature_view: FeatureView) -> "pd.DataFrame":
        """Return the latest row per entity key, used to feed materialization."""

        source = self._read(feature_view)
        keys = list(feature_view.entities)
        return (
            source.sort_values(self.event_timestamp_column)
            .groupby(keys, as_index=False)
            .tail(1)
            .reset_index(drop=True)
        )

    def write(self, feature_view: FeatureView, rows: list[dict[str, Any]]) -> int:
        """Append rows to a feature view's dataset (development helper).

        Args:
            feature_view: The target feature view.
            rows: Records to persist; each must include the entity keys and the
                event timestamp column.

        Returns:
            The number of rows written.
        """

        import pandas as pd

        frame = pd.DataFrame(rows)
        if self.event_timestamp_column not in frame.columns:
            frame[self.event_timestamp_column] = datetime.utcnow()
        frame.to_parquet(self._dataset_path(feature_view), index=False)
        return len(frame)
