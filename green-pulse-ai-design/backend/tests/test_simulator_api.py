"""
Tests for Simulator API with What-If parametric modeling and AI predictions.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_run_simulation(client):
    """Verify POST /api/v1/simulator/simulate returns predicted metrics and recommendation summary."""
    payload = {
        "production_load_percent": 115.0,
        "machine_runtime_hours": 18.0,
        "shift_schedule": "2-shift",
        "base_tariff_per_kwh": 7.50,
        "renewable_share_percent": 30.0,
    }
    response = client.post("/api/v1/simulator/simulate", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True

    data = res["data"]
    assert "predicted_energy_kwh" in data
    assert "predicted_cost_inr" in data
    assert "predicted_carbon_tons" in data
    assert "recommendation_summary" in data
    assert len(data["recommendation_summary"]) > 20
    assert len(data["hourly_comparison"]) == 24
    assert data["model_version"] == "1.2.0-prod"


def test_compare_scenarios(client):
    """Verify POST /api/v1/simulator/compare evaluates multiple scenarios."""
    scenarios = [
        {"production_load_percent": 90.0, "machine_runtime_hours": 14.0, "shift_schedule": "1-shift"},
        {"production_load_percent": 120.0, "machine_runtime_hours": 20.0, "shift_schedule": "3-shift"},
    ]
    response = client.post("/api/v1/simulator/compare", json=scenarios)
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 2
