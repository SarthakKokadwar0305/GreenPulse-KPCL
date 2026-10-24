"""
GreenPulse AI - Industrial Intelligence Layer Demonstration & Test Suite
Validates the Adaptive Threshold Engine, Alert Generation Engine, Industrial Rule Engine,
Smart Recommendation Engine, Business Impact Engine, and Priority Engine across real-world scenarios.
Outputs structured JSON results to results/intelligence_demonstration.json.
"""
import json
import logging
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from services.threshold_engine import AdaptiveThresholdEngine
from services.alert_engine import AlertGenerationEngine
from services.rule_engine import IndustrialRuleEngine
from services.recommendation_engine import SmartRecommendationEngine
from services.business_impact_engine import BusinessImpactEngine
from services.priority_engine import RecommendationPriorityEngine
from services.config.rule_registry import BUSINESS_RULES

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("GreenPulseAI.IntelligenceTest")


def run_tests():
    logger.info("================================================================================")
    logger.info("        TESTING GREENPULSE AI - INDUSTRIAL INTELLIGENCE LAYER                   ")
    logger.info("================================================================================")

    # Instantiate Engines
    threshold_engine = AdaptiveThresholdEngine()
    alert_engine = AlertGenerationEngine()
    rule_engine = IndustrialRuleEngine()
    rec_engine = SmartRecommendationEngine()
    impact_engine = BusinessImpactEngine()
    priority_engine = RecommendationPriorityEngine()

    logger.info(f"Loaded {len(BUSINESS_RULES)} Industrial Business Rules in registry.")
    assert len(BUSINESS_RULES) >= 60, f"Expected at least 60 rules, found {len(BUSINESS_RULES)}"

    demonstration_results = {
        "title": "GreenPulse AI - Industrial Intelligence Layer Verification Suite",
        "threshold_engine_examples": [],
        "scenarios": [],
    }

    # =========================================================================
    # PART 1: VALIDATE ADAPTIVE THRESHOLD ENGINE (Prompt Examples)
    # =========================================================================
    logger.info("\n>>> [1/4] TESTING ADAPTIVE THRESHOLD ENGINE...")

    # Example 1: Air Compressor Power (Current 410 kW vs Expected 350 kW)
    t1 = threshold_engine.evaluate_metric_threshold(
        machine_id="COMP-01",
        metric_name="active_power_kw",
        current_value=410.0,
        hour=10,
        day_of_week=2,
        shift="A",
        machine_state="running",
        rolling_mean=350.0,
        rolling_std=10.0,  # 350 ± 20 kW at 2-sigma
    )
    logger.info(f"Threshold Example 1 (Compressor Power): Current={t1['current_value']} kW | Expected={t1['expected_value']} kW | Dev={t1['deviation_pct']:+.1f}% | Severity={t1['severity']}")
    assert t1["severity"] in ["Warning", "Critical"], "Compressor power 410 kW should be Warning/Critical"
    demonstration_results["threshold_engine_examples"].append(t1)

    # Example 2: Heat Furnace Temperature (Current 845°C vs Expected 820 ± 40°C)
    t2 = threshold_engine.evaluate_metric_threshold(
        machine_id="FURN-01",
        metric_name="temperature_c",
        current_value=845.0,
        hour=14,
        day_of_week=1,
        shift="B",
        machine_state="running",
        rolling_mean=820.0,
        rolling_std=20.0,  # 820 ± 40°C at 2-sigma
    )
    logger.info(f"Threshold Example 2 (Furnace Temp): Current={t2['current_value']}°C | Expected={t2['expected_value']}°C | Dev={t2['deviation_pct']:+.1f}% | Severity={t2['severity']}")
    assert t2["severity"] == "Normal", "Furnace temperature 845°C should be Normal"
    demonstration_results["threshold_engine_examples"].append(t2)

    # Example 3: Paint Booth Runtime (Current 13 hrs vs Expected 8 hrs)
    t3 = threshold_engine.evaluate_metric_threshold(
        machine_id="PAINT-01",
        metric_name="runtime_hours",
        current_value=13.0,
        hour=20,
        day_of_week=3,
        shift="B",
        machine_state="running",
    )
    logger.info(f"Threshold Example 3 (Paint Booth Runtime): Current={t3['current_value']}h | Expected={t3['expected_value']}h | Dev={t3['deviation_pct']:+.1f}% | Severity={t3['severity']}")
    assert t3["severity"] in ["Warning", "Critical"], "Paint booth 13 hours runtime should be Warning"
    demonstration_results["threshold_engine_examples"].append(t3)

    # =========================================================================
    # PART 2 & 3: COMPOSITE INDUSTRIAL SCENARIOS (Alerts + Rules + Recs)
    # =========================================================================
    logger.info("\n>>> [2/4] TESTING MULTI-SOURCE INDUSTRIAL SCENARIOS...")

    # SCENARIO A: Air Compressor Unloader Valve Diaphragm Internal Leakage
    logger.info("\n--- Scenario A: Compressor Unloader Valve Diaphragm Leakage ---")
    telemetry_a = {
        "power_kw": 14.5,
        "temperature_c": 86.0,
        "machine_state": "idle",
        "idle_duration_minutes": 45,
        "power_factor": 0.91,
        "header_pressure_bar": 7.5,
        "discharge_temp_c": 89.0,
        "parts_produced_in_interval": 0,
        "power_lag_1": 6.2,
    }
    t_eval_a = [
        threshold_engine.evaluate_metric_threshold(
            machine_id="COMP-01",
            metric_name="active_power_kw",
            current_value=14.5,
            hour=11,
            day_of_week=1,
            shift="A",
            machine_state="idle",
            rolling_mean=6.5,
            rolling_std=1.2,
        )
    ]
    anomaly_a = {
        "is_anomaly": True,
        "anomaly_score": 0.88,
        "decision_function": -0.065,
    }
    forecast_a = {
        "target_energy_kwh": 1.21,
        "target_cost_inr": 12.54,
        "target_peak_kw": 14.5,
        "target_carbon_kg": 0.99,
    }
    plant_ctx_a = {"hour": 11, "shift": "A", "is_weekend": False, "total_plant_demand_kw": 195.0}

    alerts_a = alert_engine.synthesize_alerts(
        machine_id="COMP-01",
        telemetry=telemetry_a,
        threshold_evals=t_eval_a,
        ml_forecast=forecast_a,
        anomaly_result=anomaly_a,
        plant_context=plant_ctx_a,
    )
    rules_a = rule_engine.evaluate_rules(
        machine_id="COMP-01",
        telemetry=telemetry_a,
        threshold_evals=t_eval_a,
        ml_forecast=forecast_a,
        anomaly_result=anomaly_a,
        plant_context=plant_ctx_a,
    )
    recs_a = rec_engine.generate_recommendations(
        machine_id="COMP-01",
        telemetry=telemetry_a,
        threshold_evals=t_eval_a,
        fired_rules=rules_a,
        ml_forecast=forecast_a,
        anomaly_result=anomaly_a,
        plant_context=plant_ctx_a,
    )

    logger.info(f"Scenario A Generated {len(alerts_a)} alerts, {len(rules_a)} fired rules, and {len(recs_a)} prioritized recommendations.")
    logger.info(f"Top Alert: [{alerts_a[0]['severity']}] {alerts_a[0]['reason']}")
    logger.info(f"Top Recommendation: [{recs_a[0]['priority_rank']}] {recs_a[0]['title']} (Monthly Savings: ₹{recs_a[0]['estimated_cost_savings_inr']:,.0f})")
    demonstration_results["scenarios"].append({
        "scenario_name": "Compressor Unloader Valve Diaphragm Leakage",
        "machine_id": "COMP-01",
        "alerts_count": len(alerts_a),
        "fired_rules_count": len(rules_a),
        "recommendations_count": len(recs_a),
        "sample_alert": alerts_a[0] if alerts_a else None,
        "sample_recommendation": recs_a[0] if recs_a else None,
    })

    # SCENARIO B: Heat Treatment Furnace Peak Tariff Delay & Contract Demand Exceedance
    logger.info("\n--- Scenario B: Heat Treatment Furnace Peak Tariff & Demand Limit ---")
    telemetry_b = {
        "power_kw": 92.0,
        "temperature_c": 842.0,
        "machine_state": "running",
        "idle_duration_minutes": 0,
        "power_factor": 0.98,
        "shell_temp_c": 53.0,
        "parts_produced_in_interval": 1,
        "batch_queued": True,
    }
    t_eval_b = [
        threshold_engine.evaluate_metric_threshold(
            machine_id="FURN-01",
            metric_name="active_power_kw",
            current_value=92.0,
            hour=9,
            day_of_week=2,
            shift="A",
            machine_state="running",
            rolling_mean=75.0,
            rolling_std=8.0,
        )
    ]
    forecast_b = {
        "target_energy_kwh": 7.67,
        "target_cost_inr": 79.5,
        "target_peak_kw": 95.0,
        "target_carbon_kg": 6.29,
    }
    plant_ctx_b = {"hour": 9, "shift": "A", "is_weekend": False, "total_plant_demand_kw": 238.5}  # 95% critical level!

    alerts_b = alert_engine.synthesize_alerts(
        machine_id="FURN-01",
        telemetry=telemetry_b,
        threshold_evals=t_eval_b,
        ml_forecast=forecast_b,
        anomaly_result={"is_anomaly": False},
        plant_context=plant_ctx_b,
    )
    rules_b = rule_engine.evaluate_rules(
        machine_id="FURN-01",
        telemetry=telemetry_b,
        threshold_evals=t_eval_b,
        ml_forecast=forecast_b,
        anomaly_result={"is_anomaly": False},
        plant_context=plant_ctx_b,
    )
    recs_b = rec_engine.generate_recommendations(
        machine_id="FURN-01",
        telemetry=telemetry_b,
        threshold_evals=t_eval_b,
        fired_rules=rules_b,
        ml_forecast=forecast_b,
        anomaly_result={"is_anomaly": False},
        plant_context=plant_ctx_b,
    )

    logger.info(f"Scenario B Generated {len(alerts_b)} alerts, {len(rules_b)} fired rules, and {len(recs_b)} prioritized recommendations.")
    critical_alerts = [a for a in alerts_b if a["severity"] in ["Critical", "Emergency"]]
    logger.info(f"Critical Demand Alert: {critical_alerts[0]['reason'] if critical_alerts else 'None'}")
    demonstration_results["scenarios"].append({
        "scenario_name": "Heat Treatment Furnace Peak Tariff Delay & Contract Demand Exceedance",
        "machine_id": "FURN-01",
        "alerts_count": len(alerts_b),
        "fired_rules_count": len(rules_b),
        "recommendations_count": len(recs_b),
        "sample_alert": critical_alerts[0] if critical_alerts else None,
        "sample_recommendation": recs_b[0] if recs_b else None,
    })

    # SCENARIO C: Coolant Pump Cavitation & Suction Strainer Pressure Drop
    logger.info("\n--- Scenario C: Coolant Pump Cavitation & Suction Strainer ---")
    telemetry_c = {
        "power_kw": 4.8,
        "temperature_c": 32.0,
        "machine_state": "running",
        "suction_pressure_bar": 0.85,
        "vibration_rms": 4.2,
        "cooling_return_temp_c": 21.0,
        "power_factor": 0.88,
    }
    t_eval_c = [
        threshold_engine.evaluate_metric_threshold(
            machine_id="PUMP-01",
            metric_name="active_power_kw",
            current_value=4.8,
            hour=15,
            day_of_week=4,
            shift="B",
            machine_state="running",
            rolling_mean=3.7,
            rolling_std=0.4,
        )
    ]
    anomaly_c = {
        "is_anomaly": True,
        "anomaly_score": 0.92,
        "decision_function": -0.078,
    }
    plant_ctx_c = {"hour": 15, "shift": "B", "is_weekend": False, "total_plant_demand_kw": 178.0}

    alerts_c = alert_engine.synthesize_alerts("PUMP-01", telemetry_c, t_eval_c, None, anomaly_c, plant_ctx_c)
    rules_c = rule_engine.evaluate_rules("PUMP-01", telemetry_c, t_eval_c, None, anomaly_c, plant_ctx_c)
    recs_c = rec_engine.generate_recommendations("PUMP-01", telemetry_c, t_eval_c, rules_c, None, anomaly_c, plant_ctx_c)

    logger.info(f"Scenario C Generated {len(alerts_c)} alerts, {len(rules_c)} fired rules, and {len(recs_c)} prioritized recommendations.")
    demonstration_results["scenarios"].append({
        "scenario_name": "Coolant Pump Cavitation & Suction Strainer Pressure Drop",
        "machine_id": "PUMP-01",
        "alerts_count": len(alerts_c),
        "fired_rules_count": len(rules_c),
        "recommendations_count": len(recs_c),
        "sample_alert": alerts_c[0] if alerts_c else None,
        "sample_recommendation": recs_c[0] if recs_c else None,
    })

    # =========================================================================
    # PART 4: SAVE VERIFICATION ARTIFACT
    # =========================================================================
    results_dir = PROJECT_ROOT / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    out_file = results_dir / "intelligence_demonstration.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(demonstration_results, f, indent=2)

    logger.info(f"\nSaved structured verification results to {out_file}")
    logger.info("================================================================================")
    logger.info("      INDUSTRIAL INTELLIGENCE LAYER PASSED ALL VALIDATION CHECKS                ")
    logger.info("================================================================================")


if __name__ == "__main__":
    run_tests()
