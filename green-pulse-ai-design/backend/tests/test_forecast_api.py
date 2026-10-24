"""
Tests for Forecast API with SHAP Explainability & Confidence Metrics.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_get_forecast_default_24h(client):
    """Verify GET /api/v1/forecast returns 24h forecast with SHAP explanations."""
    response = client.get("/api/v1/forecast?horizon=24")
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True

    data = payload["data"]
    assert data["forecast_range"] == "Next 24 Hours"
    assert data["projected_day_energy_kwh"] > 0
    assert data["projected_cost"] > 0
    assert data["projected_carbon_tons"] > 0
    assert len(data["hourly_forecast"]) == 24

    # Verify AI Explainability & Versioning
    assert data["model_version"] == "1.2.0-prod"
    assert data["confidence_score"] >= 0.90
    assert "shap_explanation" in data
    shap_info = data["shap_explanation"]
    assert len(shap_info["top_contributing_features"]) > 0
    assert "natural_language_explanation" in shap_info
    assert len(shap_info["natural_language_explanation"]) > 10


def test_get_forecast_machine_filtered(client):
    """Verify forecast filtered by machine_id."""
    response = client.get("/api/v1/forecast?horizon=12&machine_id=COMP-01")
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data["hourly_forecast"]) == 12
    assert data["model_architecture"] is not None


def test_get_forecast_invalid_horizon(client):
    """Verify validation error on out-of-range horizon (> 168 hours)."""
    response = client.get("/api/v1/forecast?horizon=200")
    assert response.status_code == 422
