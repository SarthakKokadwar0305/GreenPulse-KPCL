"""
Tests for the 6 Industrial Intelligence Engines and 60 Industrial Business Rules.
"""
import pytest
from services.threshold_engine import AdaptiveThresholdEngine
from services.alert_engine import AlertGenerationEngine
from services.rule_engine import IndustrialRuleEngine
from services.recommendation_engine import SmartRecommendationEngine
from services.business_impact_engine import BusinessImpactEngine
from services.priority_engine import RecommendationPriorityEngine
from services.config.rule_registry import BUSINESS_RULES


def test_rule_registry_count():
    """Verify registry contains all 60 industrial business rules."""
    assert len(BUSINESS_RULES) == 60
    modules = set(r["module"] for r in BUSINESS_RULES)
    assert len(modules) == 6
    assert "EnergyEfficiencyRules" in modules
    assert "TariffOptimizationRules" in modules
    assert "EquipmentHealthRules" in modules
    assert "DemandManagementRules" in modules
    assert "CarbonSustainabilityRules" in modules
    assert "ProductionAlignmentRules" in modules


def test_adaptive_threshold_compressor_power():
    """Verify adaptive threshold evaluation on compressor power excursion."""
    engine = AdaptiveThresholdEngine()
    t = engine.evaluate_metric_threshold(
        machine_id="COMP-01",
        metric_name="active_power_kw",
        current_value=410.0,
        hour=10,
        day_of_week=2,
        shift="A",
        machine_state="running",
        rolling_mean=350.0,
        rolling_std=10.0,
    )
    assert t["severity"] in ["Warning", "Critical"]
    assert t["deviation"] == 60.0
    assert t["deviation_pct"] > 15.0
    assert t["confidence"] > 0.90


def test_adaptive_threshold_furnace_temp_normal():
    """Verify furnace temperature operating in normal band."""
    engine = AdaptiveThresholdEngine()
    t = engine.evaluate_metric_threshold(
        machine_id="FURN-01",
        metric_name="temperature_c",
        current_value=845.0,
        hour=14,
        day_of_week=1,
        shift="B",
        machine_state="running",
        rolling_mean=820.0,
        rolling_std=20.0,
    )
    assert t["severity"] == "Normal"
    assert t["deviation_pct"] < 5.0


def test_alert_generation_contract_limit():
    """Verify alert engine synthesizes emergency contract limit alert."""
    engine = AlertGenerationEngine()
    telemetry = {"power_kw": 90.0, "machine_state": "running"}
    alerts = engine.synthesize_alerts(
        machine_id="FURN-01",
        telemetry=telemetry,
        threshold_evals=[],
        plant_context={"total_plant_demand_kw": 239.0, "hour": 10, "shift": "A"}
    )
    demand_alerts = [a for a in alerts if "CONTRACT_DEMAND" in a["alert_type"]]
    assert len(demand_alerts) > 0
    assert demand_alerts[0]["severity"] == "Emergency"
    assert demand_alerts[0]["priority"] == "Critical"


def test_business_impact_calculations():
    """Verify financial OPEX savings, carbon reduction, and payback period calculation."""
    engine = BusinessImpactEngine()
    impact = engine.calculate_impact(
        hourly_kwh_saved=20.0,
        daily_operating_hours_affected=16.0,
        avoided_downtime_hours_per_month=2.0,
        capex_inr=15000.0,
        risk_level="High Risk Reduction",
    )
    assert impact["energy_savings"]["monthly_kwh"] > 0
    assert impact["financial_savings"]["monthly_total_savings_inr"] > 50000.0
    assert impact["carbon_reduction"]["annual_carbon_tonnes_co2e"] > 0
    assert "months" in impact["investment_economics"]["payback_period"]


def test_priority_engine_ranking():
    """Verify multi-criteria priority engine orders recommendations properly."""
    engine = RecommendationPriorityEngine()
    recs = [
        {"title": "Low Priority Lighting Adjustment", "priority": "Low", "machine_criticality": 2, "confidence": 0.85, "estimated_cost_savings_inr": 2000.0},
        {"title": "Emergency Compressor Valve Overhaul", "priority": "Critical", "machine_criticality": 5, "confidence": 0.96, "estimated_cost_savings_inr": 95000.0, "estimated_energy_savings_kwh": 8500.0},
    ]
    ranked = engine.rank_recommendations(recs)
    assert len(ranked) == 2
    assert ranked[0]["title"] == "Emergency Compressor Valve Overhaul"
    assert ranked[0]["priority_rank"] == "CRITICAL_IMMEDIATE"
    assert ranked[0]["priority_score"] > ranked[1]["priority_score"]
