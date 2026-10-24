"""
Tests for Recommendations API with Business Reasoning, ROI, and Supporting Rules.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_list_recommendations(client):
    """Verify GET /api/v1/recommendations returns prescriptive measures."""
    response = client.get("/api/v1/recommendations")
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True

    recs = payload["data"]
    assert len(recs) > 0
    first = recs[0]
    assert "title" in first
    assert "priority" in first
    assert "estimated_savings_currency_per_month" in first
    assert "estimated_carbon_reduction_tons_per_month" in first
    assert "roi_percent" in first
    assert "business_explanation" in first
    assert "technical_explanation" in first
    assert "supporting_rule_ids" in first
    assert len(first["supporting_rule_ids"]) > 0


def test_apply_recommendation(client):
    """Verify POST /api/v1/recommendations/{id}/apply commits strategy."""
    response = client.post(
        "/api/v1/recommendations/rec-01/apply",
        json={"applied_by": "Plant Chief Engineer", "override_parameters": {}}
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["applied"] is True
    assert data["applied_at"] is not None
