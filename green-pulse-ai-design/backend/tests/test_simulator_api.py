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


def test_machine_simulation_running(client):
    """Verify POST /api/v1/simulator/machine runs interactive machine digital twin simulation."""
    payload = {
        "machine_id": "air-compressor",
        "machine_state": "running",
        "runtime_hours": 14.0,
        "production_load_percent": 85.0,
        "motor_speed_percent": 85.0,
        "temperature_c": 78.0,
        "voltage_v": 400.0,
        "current_a": 520.0,
        "power_factor": 0.94,
        "renewable_share_percent": 35.0,
        "maintenance_condition": "excellent",
    }
    response = client.post("/api/v1/simulator/machine", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True

    data = res["data"]
    assert data["machine_id"] == "air-compressor"
    assert data["predicted_power_kw"] > 0
    assert data["predicted_energy_kwh"] > 0
    assert data["machine_health_percent"] >= 70
    assert data["equipment_efficiency_percent"] > 80
    assert "remaining_useful_life_days" in data
    assert "oee_percent" in data
    assert len(data["explanations"]) > 0
    assert len(data["prescriptive_insights"]) > 0
    assert len(data["hourly_power_profile"]) == 24


def test_machine_simulation_emergency_stop(client):
    """Verify emergency stop throttles active power to standby and flags operational risk."""
    payload = {
        "machine_id": "heat-furnace",
        "machine_state": "emergency_stop",
        "runtime_hours": 0.0,
        "production_load_percent": 0.0,
        "motor_speed_percent": 0.0,
        "temperature_c": 840.0,
        "voltage_v": 400.0,
        "current_a": 5.0,
        "power_factor": 0.70,
        "renewable_share_percent": 22.0,
        "maintenance_condition": "good",
    }
    response = client.post("/api/v1/simulator/machine", json=payload)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["predicted_power_kw"] <= 1.0
    assert data["equipment_efficiency_percent"] == 0.0
    assert data["operational_risk"] == "Severe"


def test_machine_simulation_high_temp(client):
    """Verify temperature exceeding threshold increases failure probability."""
    payload = {
        "machine_id": "air-compressor",
        "machine_state": "running",
        "runtime_hours": 16.0,
        "production_load_percent": 100.0,
        "motor_speed_percent": 100.0,
        "temperature_c": 108.0,  # Far above 90°C thermal threshold
        "voltage_v": 400.0,
        "current_a": 650.0,
        "power_factor": 0.88,
        "renewable_share_percent": 22.0,
        "maintenance_condition": "warning",
    }
    response = client.post("/api/v1/simulator/machine", json=payload)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["failure_probability_percent"] > 30.0
    assert data["operational_risk"] in ["High", "Severe"]


def test_machine_simulation_history_audit(client):
    """Verify saving and retrieving simulation timeline audit entries."""
    entry = {
        "timestamp": "2026-10-25 10:15:00",
        "machine_id": "air-compressor",
        "machine_name": "Air Compressor 01 (Lead)",
        "changed_parameters": ["Runtime: 16h → 12h", "Load: 100% → 85%"],
        "previous_values": {"runtime_hours": 16.0},
        "predicted_values": {"predicted_energy_kwh": 2600.0},
        "user": "Test Engineer",
    }
    post_res = client.post("/api/v1/simulator/machine/history", json=entry)
    assert post_res.status_code == 200
    saved = post_res.json()["data"]
    assert saved["id"] is not None

    get_res = client.get("/api/v1/simulator/machine/history?limit=10")
    assert get_res.status_code == 200
    timeline = get_res.json()["data"]
    assert len(timeline) >= 1

