"""
GreenPulse AI - Industrial AI Validation Pipeline & Report Generator
Validates end-to-end integration across:
1. Forecast API (XGBoost + SHAP Explainability)
2. Anomaly API (Isolation Forest + Severity Engine)
3. Recommendation API (MCDA Engine + Financial Impact)
4. Simulator API (Parametric Counterfactuals + Model Inference)
5. Threshold Engine (Dynamic Industrial Limits)
6. Alert Engine (Multi-tier Alerting & SLA Tracking)
7. Rule Engine (Deterministic Domain Rules)
8. Model Registry & Latency Benchmarks
"""

import sys
import os
import json
import time
from datetime import datetime, timezone
from pathlib import Path

# Setup paths
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
BACKEND_DIR = PROJECT_ROOT / "backend"

for p in [str(PROJECT_ROOT), str(BACKEND_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from fastapi.testclient import TestClient
from app.main import app
from app.ml.model_registry import ModelRegistry
from services.threshold_engine import AdaptiveThresholdEngine
from services.alert_engine import AlertGenerationEngine
from services.rule_engine import IndustrialRuleEngine
from services.recommendation_engine import SmartRecommendationEngine
from services.business_impact_engine import BusinessImpactEngine
from services.priority_engine import RecommendationPriorityEngine

def run_validation():
    print("=================================================================")
    print("GreenPulse AI - Industrial AI Integration Validation Suite")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print("=================================================================\n")
    
    validation_results = {
        "metadata": {
            "platform": "GreenPulse AI Industrial Energy Platform",
            "validation_timestamp": datetime.now(timezone.utc).isoformat(),
            "environment": "production-validation",
            "model_version": "1.2.0-prod",
            "status": "PASSED"
        },
        "components": {},
        "benchmarks": {},
        "summary": {}
    }
    
    all_passed = True
    
    # 1. Model Registry Validation
    print("[1/8] Validating Model Registry...")
    registry_start = time.perf_counter()
    registry = ModelRegistry.get_instance()
    reg_models = registry.get_all_models()
    registry_latency_ms = (time.perf_counter() - registry_start) * 1000
    
    expected_models = [
        "energy_forecast", "cost_forecast", "carbon_forecast", 
        "peak_forecast", "anomaly_detector", "scaler", "encoder"
    ]
    missing_models = [m for m in expected_models if m not in reg_models or reg_models[m] is None]
    reg_status = "PASSED" if not missing_models else "FAILED"
    if missing_models:
        all_passed = False
        
    validation_results["components"]["model_registry"] = {
        "status": reg_status,
        "loaded_models_count": len([m for m in reg_models if reg_models[m] is not None]),
        "expected_models": expected_models,
        "missing_models": missing_models,
        "singleton_verified": registry is ModelRegistry.get_instance(),
        "metadata_loaded": len(registry._metadata.get("models", {})),
        "latency_ms": round(registry_latency_ms, 3)
    }
    print(f"      -> Status: {reg_status} | Loaded: {len(reg_models)} artifacts | Latency: {registry_latency_ms:.2f}ms")
    
    # 2. Threshold Engine Validation
    print("[2/8] Validating Adaptive Threshold Engine...")
    te_start = time.perf_counter()
    te = registry.threshold_engine or AdaptiveThresholdEngine()
    
    normal_eval = te.evaluate_metric_threshold(
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
    breach_eval = te.evaluate_metric_threshold(
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
    te_latency_ms = (time.perf_counter() - te_start) * 1000
    
    te_status = "PASSED" if normal_eval["severity"] == "Normal" and breach_eval["severity"] in ["Warning", "Critical"] else "FAILED"
    if te_status != "PASSED":
        all_passed = False
        
    validation_results["components"]["threshold_engine"] = {
        "status": te_status,
        "normal_test_severity": normal_eval["severity"],
        "breach_test_severity": breach_eval["severity"],
        "breach_deviation_pct": breach_eval["deviation_pct"],
        "confidence": breach_eval["confidence"],
        "latency_ms": round(te_latency_ms, 3)
    }
    print(f"      -> Status: {te_status} | Severity: {breach_eval['severity']} (Dev: {breach_eval['deviation_pct']}%) | Latency: {te_latency_ms:.2f}ms")

    # 3. Rule Engine Validation
    print("[3/8] Validating Industrial Rule Engine (60 Rules)...")
    re_start = time.perf_counter()
    re = registry.rule_engine or IndustrialRuleEngine()
    
    telemetry_sample = {
        "active_power_kw": 410.0,
        "power_kw": 410.0,
        "power_factor": 0.81,
        "temperature_c": 920.0,
        "machine_state": "running",
        "load_ratio": 0.95,
        "is_idle": False
    }
    plant_ctx = {"total_plant_demand_kw": 240.0, "hour": 19, "shift": "B", "is_weekend": False}
    rule_evals = re.evaluate_rules(
        machine_id="COMP-01",
        telemetry=telemetry_sample,
        threshold_evals=[breach_eval],
        plant_context=plant_ctx
    )
    re_latency_ms = (time.perf_counter() - re_start) * 1000
    
    re_status = "PASSED" if len(rule_evals) > 0 else "FAILED"
    if re_status != "PASSED":
        all_passed = False
        
    validation_results["components"]["rule_engine"] = {
        "status": re_status,
        "total_domain_rules_registered": len(re.rules),
        "triggered_rules_count": len(rule_evals),
        "triggered_rule_ids": [r.get("rule_id") for r in rule_evals],
        "latency_ms": round(re_latency_ms, 3)
    }
    print(f"      -> Status: {re_status} | Triggered rules: {len(rule_evals)} / {len(re.rules)} | Latency: {re_latency_ms:.2f}ms")

    # 4. Alert Engine Validation
    print("[4/8] Validating Alert Generation Engine...")
    ae_start = time.perf_counter()
    ae = registry.alert_engine or AlertGenerationEngine()
    alerts = ae.synthesize_alerts(
        machine_id="FURN-01",
        telemetry={"power_kw": 95.0, "machine_state": "running"},
        threshold_evals=[],
        plant_context={"total_plant_demand_kw": 245.0, "hour": 10, "shift": "A"}
    )
    ae_latency_ms = (time.perf_counter() - ae_start) * 1000
    
    ae_status = "PASSED" if len(alerts) > 0 else "FAILED"
    if ae_status != "PASSED":
        all_passed = False
        
    validation_results["components"]["alert_engine"] = {
        "status": ae_status,
        "alerts_generated_count": len(alerts),
        "alert_types": [a.get("alert_type") for a in alerts],
        "highest_severity": alerts[0].get("severity") if alerts else None,
        "latency_ms": round(ae_latency_ms, 3)
    }
    print(f"      -> Status: {ae_status} | Generated: {len(alerts)} alerts | Latency: {ae_latency_ms:.2f}ms")

    # API Integration Validations
    with TestClient(app) as client:
        # 5. Forecast API Validation
        print("[5/8] Validating Forecast API & SHAP Explainability...")
        fc_start = time.perf_counter()
        fc_resp = client.get("/api/v1/forecast?horizon=24")
        fc_latency_ms = (time.perf_counter() - fc_start) * 1000
        
        fc_payload = fc_resp.json()
        fc_data = fc_payload.get("data", {}) if isinstance(fc_payload, dict) else {}
        has_shap = "shap_explanation" in fc_data and fc_data["shap_explanation"] is not None
        has_features = "feature_importance" in fc_data and len(fc_data.get("feature_importance", [])) > 0
        has_confidence = "confidence_score" in fc_data
        
        fc_status = "PASSED" if fc_resp.status_code == 200 and has_shap and has_features and has_confidence else "FAILED"
        if fc_status != "PASSED":
            all_passed = False
            
        validation_results["components"]["forecast_api"] = {
            "status": fc_status,
            "http_status": fc_resp.status_code,
            "horizon_hours": len(fc_data.get("hourly_forecast", [])),
            "shap_explanation_present": has_shap,
            "natural_language_summary": fc_data.get("shap_explanation", {}).get("natural_language_explanation", "")[:120] if has_shap else None,
            "top_features_count": len(fc_data.get("feature_importance", [])),
            "confidence_score": fc_data.get("confidence_score"),
            "model_version": fc_data.get("model_version"),
            "latency_ms": round(fc_latency_ms, 3)
        }
        print(f"      -> Status: {fc_status} | HTTP: {fc_resp.status_code} | SHAP: {has_shap} | Latency: {fc_latency_ms:.2f}ms")

        # 6. Anomaly API Validation
        print("[6/8] Validating Anomaly API & Severity Engine...")
        an_start = time.perf_counter()
        an_resp = client.get("/api/v1/anomaly")
        an_latency_ms = (time.perf_counter() - an_start) * 1000
        
        an_payload = an_resp.json()
        an_incidents = an_payload.get("data", []) if isinstance(an_payload, dict) else []
        sample_inc = an_incidents[0] if an_incidents else {}
        
        has_anomaly_score = "anomaly_score" in sample_inc
        has_root_cause = "root_cause" in sample_inc
        has_suggested_action = "suggested_action" in sample_inc
        
        an_status = "PASSED" if an_resp.status_code == 200 and len(an_incidents) > 0 and has_anomaly_score else "FAILED"
        if an_status != "PASSED":
            all_passed = False
            
        validation_results["components"]["anomaly_api"] = {
            "status": an_status,
            "http_status": an_resp.status_code,
            "incident_count": len(an_incidents),
            "sample_anomaly_score": sample_inc.get("anomaly_score"),
            "sample_root_cause": sample_inc.get("root_cause"),
            "sample_suggested_action": sample_inc.get("suggested_action"),
            "sample_threshold_violated": sample_inc.get("threshold_violated"),
            "latency_ms": round(an_latency_ms, 3)
        }
        print(f"      -> Status: {an_status} | HTTP: {an_resp.status_code} | Incidents: {len(an_incidents)} | Latency: {an_latency_ms:.2f}ms")

        # 7. Recommendation API Validation
        print("[7/8] Validating Recommendation API & ROI Quantification...")
        rc_start = time.perf_counter()
        rc_resp = client.get("/api/v1/recommendations")
        rc_latency_ms = (time.perf_counter() - rc_start) * 1000
        
        rc_payload = rc_resp.json()
        rc_items = rc_payload.get("data", []) if isinstance(rc_payload, dict) else []
        sample_rec = rc_items[0] if rc_items else {}
        
        has_business_explanation = "business_explanation" in sample_rec
        has_savings = "estimated_savings_currency_per_month" in sample_rec or "estimated_energy_savings_kwh" in sample_rec
        has_roi = "roi_percent" in sample_rec
        
        rc_status = "PASSED" if rc_resp.status_code == 200 and len(rc_items) > 0 and has_business_explanation and has_roi else "FAILED"
        if rc_status != "PASSED":
            all_passed = False
            
        validation_results["components"]["recommendation_api"] = {
            "status": rc_status,
            "http_status": rc_resp.status_code,
            "recommendation_count": len(rc_items),
            "sample_title": sample_rec.get("title"),
            "sample_priority": sample_rec.get("priority"),
            "sample_business_explanation": sample_rec.get("business_explanation"),
            "sample_roi_percent": sample_rec.get("roi_percent"),
            "latency_ms": round(rc_latency_ms, 3)
        }
        print(f"      -> Status: {rc_status} | HTTP: {rc_resp.status_code} | Count: {len(rc_items)} | Latency: {rc_latency_ms:.2f}ms")

        # 8. Simulator API Validation
        print("[8/8] Validating Simulator API & Parametric Counterfactuals...")
        sim_start = time.perf_counter()
        sim_payload = {
            "production_load_percent": 115.0,
            "machine_runtime_hours": 18.0,
            "shift_schedule": "2-shift",
            "base_tariff_per_kwh": 8.0,
            "renewable_share_percent": 25.0
        }
        sim_resp = client.post("/api/v1/simulator/simulate", json=sim_payload)
        sim_latency_ms = (time.perf_counter() - sim_start) * 1000
        
        sim_payload_resp = sim_resp.json()
        sim_data = sim_payload_resp.get("data", {}) if isinstance(sim_payload_resp, dict) else {}
        has_energy = "predicted_energy_kwh" in sim_data
        has_cost = "predicted_cost_inr" in sim_data
        has_carbon = "predicted_carbon_tons" in sim_data
        has_summary = "recommendation_summary" in sim_data
        
        sim_status = "PASSED" if sim_resp.status_code == 200 and has_energy and has_cost and has_carbon and has_summary else "FAILED"
        if sim_status != "PASSED":
            all_passed = False
            
        validation_results["components"]["simulator_api"] = {
            "status": sim_status,
            "http_status": sim_resp.status_code,
            "predicted_energy_kwh": sim_data.get("predicted_energy_kwh"),
            "predicted_cost_inr": sim_data.get("predicted_cost_inr"),
            "predicted_carbon_tons": sim_data.get("predicted_carbon_tons"),
            "savings_inr": sim_data.get("savings_inr"),
            "recommendation_summary": sim_data.get("recommendation_summary"),
            "latency_ms": round(sim_latency_ms, 3)
        }
        print(f"      -> Status: {sim_status} | HTTP: {sim_resp.status_code} | Cost: INR {sim_data.get('predicted_cost_inr')} | Latency: {sim_latency_ms:.2f}ms")

    # Benchmarks & Summary
    validation_results["benchmarks"] = {
        "model_registry_lookup_ms": validation_results["components"]["model_registry"]["latency_ms"],
        "threshold_engine_eval_ms": validation_results["components"]["threshold_engine"]["latency_ms"],
        "rule_engine_eval_ms": validation_results["components"]["rule_engine"]["latency_ms"],
        "alert_engine_eval_ms": validation_results["components"]["alert_engine"]["latency_ms"],
        "forecast_api_inference_ms": validation_results["components"]["forecast_api"]["latency_ms"],
        "anomaly_api_inference_ms": validation_results["components"]["anomaly_api"]["latency_ms"],
        "recommendation_api_latency_ms": validation_results["components"]["recommendation_api"]["latency_ms"],
        "simulator_api_latency_ms": validation_results["components"]["simulator_api"]["latency_ms"],
        "average_api_latency_ms": round(
            (validation_results["components"]["forecast_api"]["latency_ms"] +
             validation_results["components"]["anomaly_api"]["latency_ms"] +
             validation_results["components"]["recommendation_api"]["latency_ms"] +
             validation_results["components"]["simulator_api"]["latency_ms"]) / 4.0, 3
        )
    }

    validation_results["summary"] = {
        "total_components_validated": len(validation_results["components"]),
        "passed_components": sum(1 for c in validation_results["components"].values() if c["status"] == "PASSED"),
        "failed_components": sum(1 for c in validation_results["components"].values() if c["status"] != "PASSED"),
        "overall_status": "PASSED" if all_passed else "FAILED"
    }

    # Save validation report
    output_paths = [
        PROJECT_ROOT / "results" / "validation_report.json",
        BACKEND_DIR / "results" / "validation_report.json"
    ]
    for p in output_paths:
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(validation_results, f, indent=2)
        print(f"\n[REPORT] Saved validation report -> {p}")

    print("\n=================================================================")
    print(f"Validation Outcome: {validation_results['summary']['overall_status']}")
    print(f"Passed: {validation_results['summary']['passed_components']} / {validation_results['summary']['total_components_validated']}")
    print("=================================================================\n")
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(run_validation())
