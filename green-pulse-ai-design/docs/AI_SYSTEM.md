# GreenPulse AI - Industrial AI System Architecture

## 1. Executive Summary

**GreenPulse AI** is a production-grade Industrial Energy Intelligence Platform designed for high-throughput manufacturing facilities. The platform bridges the gap between raw Industrial Internet of Things (IIoT) telemetry, machine learning models, and actionable plant engineering decisions.

Rather than treating machine learning as a black box that emits isolated numbers (e.g. `energy = 3840 kWh`), GreenPulse AI synthesizes:
1. **Multi-Target Machine Learning Regressors** for energy, cost, carbon, and peak demand.
2. **Explainable AI (TreeExplainer SHAP)** generating natural language business narratives and attribution vectors.
3. **Adaptive Threshold Engine** dynamically calculating operational limits based on shift schedules, equipment state, and rolling statistics.
4. **Industrial Rule Engine** evaluating 60 deterministic domain rules across 6 operational modules.
5. **Prescriptive Recommendation Engine** performing Multi-Criteria Decision Analysis (MCDA) to quantify financial ROI and carbon abatement.

```
+-----------------------------------------------------------------------------------+
|                            GREENPULSE AI PLATFORM                                 |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  [ Industrial Telemetry ] ---> [ Data Preprocessing ] ---> [ Model Registry ]     |
|   - 3-Phase Power (kW)          - StandardScaler            - Singleton Loader    |
|   - Thermal Sensors (°C)        - OneHotEncoder             - Zero-Reload Cache   |
|   - Production Units            - Feature Alignment (34)    - 5 Joblib Models     |
|                                                                    |              |
|                                     +------------------------------+              |
|                                     |                                             |
|                                     v                                             |
|       +---------------------------------------------------------+                 |
|       |               INFERENCE & REASONING LAYER               |                 |
|       +---------------------------------------------------------+                 |
|       |                                                         |                 |
|       |  [ XGBoost Multi-Target ]      [ Isolation Forest ]     |                 |
|       |   - Energy Demand (kWh)         - Outlier Score         |                 |
|       |   - Cost (INR)                  - Severity Classifier   |                 |
|       |   - Carbon (tCO2e)              - Subsystem Diagnosis   |                 |
|       |   - Peak Load (kW)                                      |                 |
|       |            |                             |              |                 |
|       |            v                             v              |                 |
|       |  [ SHAP TreeExplainer ]       [ Adaptive Thresholds ]   |                 |
|       |   - Local Attributions         - Rolling 24h Baselines  |                 |
|       |   - Positive/Negative Drivers  - Diurnal & Shift Limits |                 |
|       |   - Natural Language Summary   - Deviation Tracking     |                 |
|       |            |                             |              |                 |
|       |            +--------------+--------------+              |                 |
|       |                           |                             |                 |
|       |                           v                             |                 |
|       |              [ 60 Industrial Rules ]                    |                 |
|       |               - Energy Efficiency                       |                 |
|       |               - Tariff Optimization (ToD)               |                 |
|       |               - Equipment Health & Diagnostics          |                 |
|       |               - Demand Penalty Prevention               |                 |
|       |               - Carbon Sustainability                   |                 |
|       |               - Production Load Alignment               |                 |
|       |                           |                             |                 |
|       |                           v                             |                 |
|       |          [ Prescriptive MCDA Ranking Engine ]           |                 |
|       |           - Financial OPEX Savings (INR)                |                 |
|       |           - Avoided Downtime Hours                      |                 |
|       |           - Payback Period & ROI Calculation            |                 |
|       +---------------------------------------------------------+                 |
|                                   |                                               |
|                                   v                                               |
|                    [ FastAPI Enterprise REST Endpoints ]                          |
|                     - GET  /api/v1/forecast                                       |
|                     - GET  /api/v1/anomalies                                      |
|                     - GET  /api/v1/recommendations                                |
|                     - POST /api/v1/simulator/simulate                             |
+-----------------------------------------------------------------------------------+
```

---

## 2. Multi-Horizon Forecasting Engine

The forecasting subsystem provides hourly operational demand curves across horizons up to 168 hours (7 days).

### 2.1 Model Topology
- **Algorithm**: XGBoost Regressors (`xgboost.XGBRegressor`) with Histogram-based tree method (`tree_method='hist'`).
- **Target Variables**:
  1. `energy_kwh`: Total active plant energy consumption.
  2. `cost_inr`: Financial expenditure based on Time-of-Day (ToD) tariff bands.
  3. `carbon_tons`: Scope 2 GHG emissions derived from grid carbon intensity ($0.82 \text{ kg CO}_2/\text{kWh}$).
  4. `peak_demand_kw`: 15-minute rolling maximum demand for contracted billing limit adherence.
- **Inference Optimization**: Multi-target vectorized inference processes 24 hours of predictions in $< 80 \text{ ms}$.

### 2.2 Feature Alignment Pipeline (34 Dimensions)
Raw telemetry and environmental context are normalized into a fixed 34-dimensional feature vector:
- **18 Scaled Numerical Features**: `production_units`, `machine_runtime_hours`, `ambient_temp_c`, `humidity_pct`, `grid_frequency_hz`, `power_factor`, `load_ratio`, `cooling_load_kwh`, `furnace_runtime_hours`, `motor_rpm`, `bearing_temp_c`, `vibration_mm_s`, `compressor_pressure_bar`, `operating_pressure_bar`, `flow_rate_m3_h`, `chiller_cop`, `solar_generation_kwh`, `wind_generation_kwh`.
- **15 One-Hot Encoded Categoricals**: `machine_type` (5 classes), `department` (4 classes), `shift` (3 classes: A, B, C), `tariff_period` (3 classes: Peak, Normal, Off-Peak).
- **1 Boolean Flag**: `is_weekend`.

---

## 3. Explainable AI Architecture (SHAP)

To foster trust among plant managers and energy auditors, GreenPulse AI equips every prediction with explainability generated via `shap.TreeExplainer`.

### 3.1 Explainability Artifacts
1. **Local Feature Attribution**: Quantifies how much each input feature moved the prediction from the dataset expected value ($E[f(x)]$).
2. **Directional Impact**: Classifies features into `INCREASING` (drives load upwards) or `DECREASING` (reduces load or stabilizes grid draw).
3. **Natural Language Synthesis**: Translates mathematical attributions into human-readable industrial diagnostics.
   *Example*:
   > *"Predicted demand increased because: Shift Runtime (Hours) increased by 320.50 kWh; Production Load (%) increased by 240.20 kWh; High-Temperature Furnace Runtime increased by 185.10 kWh. Offset by Solar Generation reduction of -94.30 kWh."*
4. **Visual Diagnostic Plots**:
   - `results/shap_summary_plot.png`: Global feature impact across all operating regimes.
   - `results/shap_waterfall_plot.png`: Per-prediction waterfall showing step-by-step feature contributions.

---

## 4. Industrial Reasoning Layer

The Industrial Intelligence Layer operates above the ML inference outputs, ensuring that all recommendations comply with plant physics, safety bounds, and electricity board regulations.

### 4.1 Adaptive Threshold Engine
Calculates dynamic operational boundaries rather than using static constants:
$$\mu_{\text{expected}} = \mu_{\text{baseline}} \times W_{\text{shift}} \times W_{\text{load}}$$
$$\text{Threshold}_{\text{Upper}} = \mu_{\text{expected}} + k \cdot \sigma_{\text{rolling}}$$
- Adapts to Shift A (Morning Ramp), Shift B (Peak Production), and Shift C (Night Baseload).
- Accounts for machine states: `running`, `idle`, `standby`, `maintenance`.

### 4.2 60 Industrial Business Rules
Organized into 6 domain modules:
1. **EnergyEfficiencyRules (10 Rules)**: Compressed air leak detection, chiller COP degradation, specific energy consumption (SEC) drift.
2. **TariffOptimizationRules (10 Rules)**: Peak period load shaving, battery energy storage system (BESS) dispatch, off-peak furnace preheating.
3. **EquipmentHealthRules (10 Rules)**: Motor phase current imbalance ($> 5\%$), thermal runaway in melting units, bearing vibration degradation.
4. **DemandManagementRules (10 Rules)**: Contract Demand penalty warnings ($> 85\%$ and $> 95\%$ of Contracted Maximum Demand).
5. **CarbonSustainabilityRules (10 Rules)**: Solar self-consumption optimization, renewable curtailment prevention, Scope 2 peak intensity mitigation.
6. **ProductionAlignmentRules (10 Rules)**: Machine idling during non-production shifts, batch scheduling alignment, conveyor sequencing.

### 4.3 Multi-Criteria Decision Analysis (MCDA) Ranking
Recommendations are prioritized using weighted multi-attribute utility theory:
$$\text{Score} = w_1 \cdot \text{Cost Savings} + w_2 \cdot \text{Energy Savings} + w_3 \cdot \text{Criticality} + w_4 \cdot \text{Confidence} - w_5 \cdot \text{Payback}$$
- Tiers: `CRITICAL_IMMEDIATE`, `HIGH_PRIORITY`, `MEDIUM_PRIORITY`, `LOW_PRIORITY`.

---

## 5. What-If Counterfactual Simulator

Enables plant engineers to simulate operational adjustments before making physical alterations on the shop floor:
- Adjust production load: $50\% - 150\%$
- Shift schedule modification: 1-shift, 2-shift, or 3-shift continuous
- Tariff rate adjustments: INR/kWh
- Renewable penetration: $0\% - 100\%$ solar/wind mix
- Instant evaluation of projected energy, financial impact, carbon delta, and executive recommendations.
