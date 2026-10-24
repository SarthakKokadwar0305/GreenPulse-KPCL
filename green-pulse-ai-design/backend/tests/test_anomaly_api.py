"""
Tests for Anomaly API with Isolation Forest scores, thresholds, and triggered rules.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_get_anomaly_list(client):
    """Verify GET /api/v1/anomaly returns enriched incident records."""
    response = client.get("/api/v1/anomaly")
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True

    incidents = payload["data"]
    assert len(incidents) > 0
    first = incidents[0]
    assert "anomaly_score" in first
    assert "root_cause" in first
    assert "confidence_percent" in first
    assert "suggested_action" in first
    assert "severity" in first
    assert first["model_version"] == "1.2.0-prod"


def test_get_anomalies_alias_route(client):
    """Verify GET /api/v1/anomalies alias works identically."""
    response = client.get("/api/v1/anomalies")
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert len(payload["data"]) > 0


def test_get_anomaly_filtered_by_severity(client):
    """Verify filtering by severity=critical."""
    response = client.get("/api/v1/anomaly?severity=critical")
    assert response.status_code == 200
    incidents = response.json()["data"]
    for inc in incidents:
        assert inc["severity"].lower() == "critical"
