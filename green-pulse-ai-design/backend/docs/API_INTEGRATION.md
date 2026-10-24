# GreenPulse AI - API Integration Guide & Schema Contracts

## 1. Overview

The GreenPulse AI API provides an enterprise RESTful interface exposing multi-horizon forecasting with SHAP explainability, unsupervised equipment anomaly diagnostics, prescriptive energy conservation recommendations, and parametric what-if simulations.

- **Base URL**: `http://localhost:8000/api/v1`
- **Swagger Documentation**: `http://localhost:8000/docs`
- **ReDoc Documentation**: `http://localhost:8000/redoc`
- **Standard Envelope**: All endpoints wrap payloads in a uniform response envelope (`success`, `data`, `message`, `errors`).

---

## 2. API Endpoints Specification

### 2.1 Multi-Horizon Forecast API
**`GET /forecast`**

Retrieves hourly projections for energy demand (kWh), electrical expenditure (INR), carbon emissions (tCO2e), and peak load (kW), accompanied by SHAP explainability.

#### Query Parameters:
| Parameter | Type | Required | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `horizon` | integer | No | `24` | Forecast horizon in hours (1 to 168). |
| `scenario` | string | No | `standard` | Operating scenario: `standard`, `aggressive_ramp`, `solar_curtailment`. |
| `machine_id` | string | No | `None` | Filter by specific machine (e.g. `COMP-01`, `FURN-01`). |

#### Response Example:
```json
{
  "success": true,
  "data": {
    "forecast_range": "Next 24 Hours",
    "projected_day_energy_kwh": 3840.5,
    "projected_cost": 28803.75,
    "projected_carbon_tons": 3.15,
    "peak_projected_demand_kw": 242.0,
    "confidence_score": 0.94,
    "model_version": "1.2.0-prod",
    "model_architecture": "XGBoost Multi-Target Regressors (energy, cost, carbon, peak)",
    "threshold_status": {
      "metric_name": "Peak Demand (kW)",
      "current_value": 242.0,
      "upper_limit": 260.0,
      "status": "NORMAL",
      "deviation_percent": -6.92
    },
    "feature_importance": [
      {"feature_name": "Shift Runtime (Hours)", "shap_value": 320.5, "feature_value": 18.0, "impact_type": "INCREASING"},
      {"feature_name": "Production Load (%)", "shap_value": 240.2, "feature_value": 115.0, "impact_type": "INCREASING"},
      {"feature_name": "High-Temp Furnace Runtime", "shap_value": 185.1, "feature_value": 16.0, "impact_type": "INCREASING"},
      {"feature_name": "Solar Generation", "shap_value": -94.3, "feature_value": 450.0, "impact_type": "DECREASING"}
    ],
    "shap_explanation": {
      "base_value": 3120.0,
      "prediction_value": 3840.5,
      "natural_language_explanation": "Predicted demand increased because: Shift Runtime (Hours) increased by 320.50 kWh; Production Load (%) increased by 240.20 kWh; High-Temp Furnace Runtime increased by 185.10 kWh. Offset by Solar Generation reduction of -94.30 kWh.",
      "top_contributing_features": [
        {"feature_name": "Shift Runtime (Hours)", "shap_value": 320.5, "feature_value": 18.0, "impact_type": "INCREASING"},
        {"feature_name": "Production Load (%)", "shap_value": 240.2, "feature_value": 115.0, "impact_type": "INCREASING"}
      ]
    },
    "hourly_forecast": [
      {
        "hour_offset": 1,
        "timestamp": "2026-10-24T20:00:00Z",
        "predicted_energy_kwh": 160.2,
        "upper_bound_95": 172.5,
        "lower_bound_80": 149.8,
        "projected_cost": 1201.5,
        "projected_carbon_tons": 0.131,
        "is_peak_period": false
      }
    ]
  },
  "message": "Forecast trajectory generated successfully",
  "errors": []
}
```

---

### 2.2 Anomaly Diagnostics API
**`GET /anomalies`** (Alias: **`GET /anomaly`**)

Returns detected equipment abnormalities evaluated using the Isolation Forest model and adaptive thresholds.

#### Query Parameters:
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `severity` | string | No | Filter by: `critical`, `warning`, `info`. |
| `status` | string | No | Filter by: `open`, `investigating`, `acknowledged`, `resolved`. |

#### Response Example:
```json
{
  "success": true,
  "data": [
    {
      "id": "anom-01",
      "machine_id": "COMP-01",
      "machine_name": "Main Air Compressor",
      "department": "Machining & Stamping",
      "timestamp": "2026-10-24T18:45:00Z",
      "anomaly_type": "Unscheduled Pressure Drop & Power Spike",
      "severity": "critical",
      "anomaly_score": 0.88,
      "confidence_percent": 94.5,
      "root_cause": "Intake valve leakage causing compressor motor over-amperage",
      "threshold_violated": "Active Power (410 kW > 380 kW limit)",
      "triggered_rules": [
        "RULE-EQ-001: Excessive Compressor Cycle Power",
        "RULE-EE-004: Compressed Air Pressure Gradient Excursion"
      ],
      "suggested_action": "Isolate secondary compressor manifold and inspect inlet seal.",
      "estimated_loss_rate_inr_hr": 1450.0,
      "model_version": "1.2.0-prod",
      "status": "open"
    }
  ],
  "message": "Fetched 1 anomaly incidents",
  "errors": []
}
```

---

### 2.3 Energy Conservation Recommendations API
**`GET /recommendations`**

Retrieves prioritized prescriptive actions ranked by Multi-Criteria Decision Analysis (MCDA).

#### Query Parameters:
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `category` | string | No | Filter by: `Load Shifting`, `Asset Tuning`, `Setpoint Optimization`. |

#### Response Example:
```json
{
  "success": true,
  "data": [
    {
      "id": "rec-01",
      "title": "Shift Annealing Furnace Cycle to Off-Peak Window",
      "category": "Load Shifting",
      "priority": "high",
      "potential_savings_kwh": 340.0,
      "estimated_savings_currency_per_month": 42500.0,
      "estimated_carbon_reduction_tons_per_month": 3.8,
      "roi_percent": 185.0,
      "payback_period_months": 2.5,
      "business_explanation": "Executing the 3-hour heat treatment cycle after 22:00 IST avoids the Rs 9.50/kWh peak tariff penalty.",
      "technical_explanation": "Reduces plant peak load by 140 kW during the 18:00-22:00 grid constraint window.",
      "supporting_rule_ids": ["RULE-TO-001", "RULE-DM-002"],
      "status": "active"
    }
  ],
  "message": "Fetched 1 energy conservation recommendations",
  "errors": []
}
```

---

### 2.4 Operational Simulator API
**`POST /simulator/simulate`**

Executes parametric counterfactual simulations.

#### Request Body:
```json
{
  "production_load_percent": 115.0,
  "machine_runtime_hours": 18.0,
  "shift_schedule": "2-shift",
  "base_tariff_per_kwh": 8.00,
  "renewable_share_percent": 25.0
}
```

#### Response Example:
```json
{
  "success": true,
  "data": {
    "predicted_energy_kwh": 4120.0,
    "predicted_cost_inr": 31250.0,
    "predicted_carbon_tons": 3.38,
    "savings_inr": 4500.0,
    "recommendation_summary": "Increasing renewable share to 25% offsets the 10% load increase, yielding net savings of Rs 4,500/day.",
    "model_version": "1.2.0-prod",
    "hourly_comparison": []
  },
  "message": "What-if simulation completed successfully",
  "errors": []
}
```

---

## 3. Client Integration Examples

### cURL
```bash
# 1. Fetch 24-Hour Forecast with SHAP attributions
curl -X GET "http://localhost:8000/api/v1/forecast?horizon=24" \
     -H "Accept: application/json"

# 2. Fetch Equipment Anomalies
curl -X GET "http://localhost:8000/api/v1/anomalies?severity=critical" \
     -H "Accept: application/json"

# 3. Run Parametric What-If Simulation
curl -X POST "http://localhost:8000/api/v1/simulator/simulate" \
     -H "Content-Type: application/json" \
     -d '{"production_load_percent": 110, "machine_runtime_hours": 18, "shift_schedule": "2-shift", "base_tariff_per_kwh": 7.5, "renewable_share_percent": 25}'
```

### Python (httpx)
```python
import httpx

BASE_URL = "http://localhost:8000/api/v1"

with httpx.Client(base_url=BASE_URL, timeout=10.0) as client:
    # Get Forecast
    fc = client.get("/forecast", params={"horizon": 24}).json()
    print("Projected Energy:", fc["data"]["projected_day_energy_kwh"], "kWh")
    print("SHAP Narrative:", fc["data"]["shap_explanation"]["natural_language_explanation"])

    # Run Simulation
    sim = client.post("/simulator/simulate", json={
        "production_load_percent": 115.0,
        "machine_runtime_hours": 18.0,
        "shift_schedule": "2-shift",
        "base_tariff_per_kwh": 7.50,
        "renewable_share_percent": 30.0
    }).json()
    print("Simulated Cost:", sim["data"]["predicted_cost_inr"], "INR")
```
