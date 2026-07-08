"""Tests for the health and readiness endpoints via the FastAPI TestClient."""

from fastapi.testclient import TestClient

from feature_store.main import create_app

client = TestClient(create_app())


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "version" in body


def test_ready_returns_ready():
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_list_feature_views_includes_default():
    response = client.get("/api/v1/feature-views")
    assert response.status_code == 200
    names = {view["name"] for view in response.json()}
    assert "customer_activity" in names
