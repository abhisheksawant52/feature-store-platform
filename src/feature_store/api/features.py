"""Feature serving and registry inspection endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from ..registry import FeatureRegistry
from ..serving import FeatureService
from .dependencies import get_feature_service, get_registry

router = APIRouter(prefix="/api/v1", tags=["features"])


class OnlineFeatureRequest(BaseModel):
    """Request body for the online feature retrieval endpoint."""

    features: list[str] = Field(
        ...,
        description="Feature references of the form 'view:feature'.",
        examples=[["customer_activity:transactions_7d"]],
    )
    entities: list[dict[str, Any]] = Field(
        ...,
        description="Entity key rows, e.g. [{'customer_id': 42}].",
    )


class OnlineFeatureResponse(BaseModel):
    """Response body containing the resolved feature rows."""

    results: list[dict[str, Any]]


class FeatureViewSummary(BaseModel):
    """Serializable summary of a registered feature view."""

    name: str
    entities: list[str]
    features: list[str]
    ttl_seconds: int


@router.get("/feature-views", response_model=list[FeatureViewSummary])
def list_feature_views(
    registry: FeatureRegistry = Depends(get_registry),
) -> list[FeatureViewSummary]:
    """List all feature views registered in the feature store."""

    return [
        FeatureViewSummary(
            name=view.name,
            entities=list(view.entities),
            features=[f.name for f in view.features],
            ttl_seconds=int(view.ttl.total_seconds()),
        )
        for view in registry.list_feature_views()
    ]


@router.post("/get-online-features", response_model=OnlineFeatureResponse)
def get_online_features(
    request: OnlineFeatureRequest,
    service: FeatureService = Depends(get_feature_service),
) -> OnlineFeatureResponse:
    """Return the latest online feature values for the requested entities."""

    results = service.get_online_features(request.features, request.entities)
    return OnlineFeatureResponse(results=results)
