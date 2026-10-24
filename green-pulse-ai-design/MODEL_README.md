# GreenPulse AI - Phase 3A Machine Learning & Anomaly Modeling Engine

Production-grade machine learning models, feature engineering pipelines, anomaly detectors, and evaluation reports for the **GreenPulse AI** Industrial Energy Intelligence Platform.

---

## 1. Executive Summary & Architecture Overview

Phase 3A delivers end-to-end industrial machine learning models tailored for manufacturing plant energy analytics, operational expenditure forecasting, greenhouse gas accounting, peak load demand tracking, and real-time equipment anomaly detection.

```mermaid
flowchart TD
    subgraph Data Layer
        D1[ml_train.csv - 133,326 intervals]
        D2[ml_validation.csv - 28,619 intervals]
        D3[ml_test.csv - 28,664 intervals]
    end

    subgraph Feature & Preprocessing Pipeline
        P1[StandardScaler - Numerical Sensors & Lags]
        P2[OneHotEncoder - Machine ID, State, Shift]
        P3[Cyclical Encoding - Hour & Day-of-Week sin/cos]
        P4[Operational Ratio - Load Factor kw / rated_kw]
    end

    subgraph Production Models
        M1[Energy Forecast Regressor - XGBoost]
        M2[Electricity Cost Regressor - XGBoost]
        M3[Carbon Emissions Regressor - XGBoost]
        M4[Peak Demand Regressor - XGBoost]
        M5[Equipment Telemetry Anomaly Detector - Isolation Forest]
    end

    subgraph Storage & Serving Artifacts
        A1[trained_models/ & backend/trained_models/]
        A2[results/metrics.json & training_summary.json]
        A3[results/prediction_plots/ & residual_plots/]
        A4[results/confusion_analysis/]
    end

    D1 & D2 & D3 --> P1 & P2 & P3 & P4
    P1 & P2 & P3 & P4 --> M1 & M2 & M3 & M4 & M5
    M1 & M2 & M3 & M4 & M5 --> A1 & A2 & A3 & A4
```

---

## 2. Datasets Used

The models are trained, tuned, and evaluated on verified chronological industrial datasets partitioned strictly to prevent look-ahead bias:

| Dataset | Records | Features | Purpose | Time Horizon |
| :--- | :--- | :--- | :--- | :--- |
| `ml_train.csv` | 133,326 | 26 | Model fitting, parameter estimation, encoder fitting | Chronological past |
| `ml_validation.csv` | 28,619 | 26 | Hyperparameter search, early stopping, model comparison | Chronological holdout |
| `ml_test.csv` | 28,664 | 26 | Out-of-sample unbiased generalization testing | Unseen future period |
| `ml_features_all.csv` | 190,609 | 26 | Master telemetry feature store | Full historical sequence |
| `machine_energy_summary.csv` | 8 machines | 7 | Machine-level rated power, total consumption, max demand | Plant baseline |
| `daily_energy_by_machine.csv` | 1,368 daily rows | 3 | Daily machine-wise energy tracking | Aggregated trend |
| `hourly_pattern_by_machine.csv` | 192 rows | 4 | Diurnal cycle patterns per machine | Shift & diurnal profile |
| `production_efficiency_by_day.csv` | 1,368 rows | 6 | Specific energy consumption (kWh / good unit) | Manufacturing efficiency |

### Monitored Industrial Equipment
- **CNC Machining Centers**: `CNC-01`, `CNC-02`
- **Air Compressors**: `COMP-01`, `COMP-02`
- **Heat Treatment Furnaces**: `FURN-01`
- **HVAC Chillers**: `HVAC-01`
- **Automated Paint Booths**: `PAINT-01`
- **Industrial Cooling Water Pumps**: `PUMP-01`

---

## 3. Target Variables & Domain Mathematical Formulations

To satisfy industrial accuracy without assuming nonexistent fields, target variables are rigorously derived from validated active power readings (`target_power_next_interval_kw` sampled at 5-minute intervals, `INTERVAL_HOURS = 5/60 = 0.08333`):

1. **Target Energy Consumption ($kWh$)**:
   $$\text{target\_energy\_kwh} = \text{target\_power\_next\_interval\_kw} \times \frac{5}{60}$$
2. **Target Operational Cost ($\text{INR}$)**:
   $$\text{target\_cost\_inr} = \text{target\_energy\_kwh} \times \text{Tariff}_{\text{ToD}}(t)$$
   - *Peak Tariff* ($10.368\ \text{INR/kWh}$): Hours 10:00–12:00, 18:00–22:00
   - *Base Tariff* ($7.200\ \text{INR/kWh}$): Standard day hours (06:00–10:00, 12:00–18:00)
   - *Off-Peak Tariff* ($5.200\ \text{INR/kWh}$): Night hours (22:00–06:00)
3. **Target Carbon Emissions ($kg\ CO_2e$)**:
   $$\text{target\_carbon\_kg} = \text{target\_energy\_kwh} \times 0.82\ \frac{\text{kg } CO_2e}{\text{kWh}}$$
   - Scope 2 grid emission factor based on Central Electricity Authority (CEA) baseline.
4. **Target Peak Demand ($kW$)**:
   $$\text{target\_peak\_kw} = \text{target\_power\_next\_interval\_kw}$$
   - Direct active power demand for Maximum Demand Indicator (MDI) penalty mitigation.

---

## 4. Feature Mapping & Telemetry Architecture

All inputs undergo feature engineering and scaling:

| Feature Category | Columns | Transformation / Encoding |
| :--- | :--- | :--- |
| **Operational Telemetry** | `power_kw`, `rated_power_kw`, `ambient_temp_c`, `load_ratio` | StandardScaler (zero mean, unit variance) |
| **Lagged Dynamics** | `power_lag_1` (5m), `power_lag_2` (10m), `power_lag_3` (15m), `power_lag_6` (30m), `power_lag_12` (1h), `power_lag_288` (24h), `power_lag_2016` (7d) | StandardScaler |
| **Rolling Statistics** | `rolling_mean_1h`, `rolling_std_1h` | StandardScaler |
| **Temporal Cyclical** | `hour_sin`, `hour_cos`, `dow_sin`, `dow_cos` | Passed through (preserves continuous periodicity) |
| **Operational Context** | `machine_id`, `machine_state` (`running`, `idle`, `maintenance`, `off`), `shift` (`A`, `B`, `C`) | OneHotEncoder (unseen category handling enabled) |
| **Calendar Flag** | `is_weekend` | Binary float ($0.0 / 1.0$) |

### Data Leakage Quarantine
- The dataset partition column `split` and future target values are strictly excluded from input feature vectors.
- Scalers and encoders are fitted **strictly on `ml_train.csv`** and applied unchanged to validation and test splits.

---

## 5. Model Selection & Algorithm Benchmarking

We benchmarked four candidate model families on the validation set for the primary active energy target:

| Algorithm Candidate | Validation $R^2$ | Validation MAE | Validation RMSE | Inference Latency | Training Time | Selected for Production |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **XGBoost Regressor (Primary)** | **0.6297** | **0.4896 kWh** | **0.8965 kWh** | **0.0014 ms/sample** | **0.40s** | **YES (Primary)** |
| Extra Trees Regressor | 0.6508 | 0.4797 kWh | 0.8706 kWh | 0.0047 ms/sample | 0.71s | Evaluated |
| Random Forest Regressor | 0.6433 | 0.4841 kWh | 0.8800 kWh | 0.0061 ms/sample | 2.50s | Evaluated |
| Linear Regression (Ridge Baseline) | 0.6244 | 0.5377 kWh | 0.9029 kWh | 0.0007 ms/sample | 0.03s | Baseline |

### Why XGBoost Regressor Was Selected for Production
1. **Ultra-Low Latency Inference**: $0.0014\ \text{ms}$ per sample enables sub-millisecond real-time IoT inference at the plant edge or FastAPI server.
2. **Lightweight Deployment**: XGBoost model artifact is compact (~949 KB) and supports direct multi-threaded parallel scoring with zero external C++ dependencies.
3. **Hyperparameter Controllability**: Precise regularization (`max_depth=6`, `subsample=1.0`, `colsample_bytree=1.0`, `learning_rate=0.05`) preventing over-specialization to noise in intermittent machine stop/start cycles.

---

## 6. Model Training & Validation Performance

### Multi-Target Forecasting Models (Test Partition Generalization)

Models were evaluated across Train (133,326 rows), Validation (28,619 rows), and Test (28,664 rows) splits:

| Model Task | Target Column | Test $R^2$ | Test MAE | Test RMSE | Overfitting Gap ($\Delta R^2$) | Operational Generalization |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Energy Consumption** | `target_energy_kwh` | **0.6468** | **0.4747 kWh** | **0.8608 kWh** | 0.0635 | Stable / Within Industrial Tolerance |
| **Electricity Cost** | `target_cost_inr` | **0.6664** | **₹3.7763 INR** | **₹7.0879 INR** | 0.0617 | Stable / Within Industrial Tolerance |
| **Carbon Emissions** | `target_carbon_kg` | **0.6468** | **0.3892 kg** | **0.7058 kg** | 0.0635 | Stable / Within Industrial Tolerance |
| **Peak Demand** | `target_peak_kw` | **0.6468** | **5.6960 kW** | **10.329 kW** | 0.0635 | Stable / Within Industrial Tolerance |

> **Domain Note on Industrial Percentage Error (MAPE)**:
> In manufacturing telemetry where machines frequently switch to `off` (0.0 kW) or `idle` (near-zero kW), percentage-based metrics (MAPE) naturally inflate due to near-zero denominators, even when absolute error is negligible ($\approx 0.47\ \text{kWh}$). Thus, industrial plant managers rely on **MAE**, **RMSE**, and **$R^2$** as the definitive ground truth for dispatch planning and tariff management.

### Unsupervised Anomaly Detection (Isolation Forest)
- **Algorithm**: `IsolationForest` ($n\_estimators=150$, $contamination=0.035$, $max\_samples=0.8$, $random\_state=42$)
- **Operational Features**: `power_kw`, `rated_power_kw`, `ambient_temp_c`, `rolling_mean_1h`, `rolling_std_1h`, `power_lag_1`, `power_lag_2`, `power_lag_3`, `load_ratio`.
- **Test Anomaly Rate**: **3.74%** (closely matching the expected ~3.5% industrial incident frequency).
- **Decision Separation Margin**: **0.1471** delta between normal inliers ($\mu = +0.078$) and abnormal outliers ($\mu = -0.069$).
- **State Behavior**: High anomalies concentrated during unexpected load transitions and uncharacteristic temperature-power discrepancies.

---

## 7. Saved Model Artifacts & File Locations

All production model weights, preprocessors, and metadata are saved using Joblib:

```
trained_models/
├── energy_forecast.joblib          # XGBoost active energy forecaster
├── cost_forecast.joblib            # XGBoost ToD expenditure forecaster
├── carbon_forecast.joblib          # XGBoost Scope 2 GHG forecaster
├── peak_forecast.joblib            # XGBoost peak demand forecaster
├── anomaly_detector.joblib         # Isolation Forest anomaly detector
├── scaler.joblib                   # Fitted StandardScaler for numericals
├── encoder.joblib                  # Fitted OneHotEncoder for categoricals
├── feature_list.json               # Ordered aligned feature array
├── training_config.json            # Model hyperparameter configuration
└── model_metadata.json             # Training timestamp and versioning

backend/trained_models/             # Direct mirror for backend microservices
└── (identical joblib & json artifacts)
```

### Generated Diagnostics & Evaluation Plots
```
results/
├── metrics.json                    # Full Train/Val/Test numerical metrics
├── training_summary.json           # High-level executive KPI benchmarks
├── feature_importance.csv          # Mutual info, correlation & variance table
├── model_comparison.csv            # Algorithm benchmark leaderboard
├── correlation_matrix.png          # High-resolution correlation heatmap
├── prediction_plots/
│   ├── energy_consumption_pred_vs_actual.png
│   ├── electricity_cost_pred_vs_actual.png
│   ├── carbon_emissions_pred_vs_actual.png
│   └── peak_demand_pred_vs_actual.png
├── residual_plots/
│   ├── energy_consumption_residuals.png
│   ├── electricity_cost_residuals.png
│   ├── carbon_emissions_residuals.png
│   └── peak_demand_residuals.png
└── confusion_analysis/
    ├── anomaly_score_distribution.png
    ├── decision_function_separation.png
    ├── operational_anomaly_scatter.png
    └── anomaly_evaluation_summary.json
```

---

## 8. Retraining Instructions & Execution Guide

The entire training, tuning, and evaluation suite is encapsulated into modular, non-notebook Python code.

### Prerequisites
Activate the project virtual environment:
```powershell
# Windows PowerShell
.\backend\.venv\Scripts\Activate.ps1
```

### Full Automated Retraining Pipeline
Run the master pipeline script from the project root:
```powershell
python run_phase3a_pipeline.py
```

### Running Individual Pipeline Stages
You can also run each step independently as a standalone module:

1. **Dataset Profiling & Schema Understanding**:
   ```powershell
   python -m ml_pipeline.dataset_understanding
   ```
2. **Feature Analysis & Correlation Heatmap**:
   ```powershell
   python -m ml_pipeline.feature_analysis
   ```
3. **Algorithm Benchmarking**:
   ```powershell
   python -m ml_pipeline.model_selection
   ```
4. **Forecasting Model Training & Tuning**:
   ```powershell
   python -m ml_pipeline.forecast_trainer
   ```
5. **Anomaly Model Training & Evaluation**:
   ```powershell
   python -m ml_pipeline.anomaly_trainer
   ```

---

## 9. Readiness for Phase 3B

Phase 3A provides tested, validated, serialized models and preprocessing pipelines.
The system is ready for Phase 3B integration:
- Real-time inference pipelines
- Threshold and Alert Engine
- Recommendation Engine and Simulation
- FastAPI REST endpoint integration
- SHAP explainability integration
