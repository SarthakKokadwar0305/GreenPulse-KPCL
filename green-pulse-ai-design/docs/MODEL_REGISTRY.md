# GreenPulse AI - Centralized Model Registry Specification

## 1. Overview & Architecture

The **Model Registry** is the single source of truth for all serialized machine learning models, preprocessors, and domain reasoning engines within the GreenPulse AI platform.

### Design Principles:
- **Zero Per-Request Reloading**: All Joblib artifacts are deserialized into memory once during FastAPI application startup via the lifespan context manager.
- **Thread-Safe Singleton Access**: The `ModelRegistry` class guarantees that all API requests share immutable, cached model instances, preventing memory leaks and CPU spikes.
- **Cryptographic Provenance**: Every model file is verified with SHA-256 hashing to prevent tampering or corruption during deployment.
- **Unified Interface**: Preprocessors, forecasting regressors, anomaly detectors, and rule engines are accessible through a uniform API.

---

## 2. Model Inventory & Cryptographic Verification

| Artifact Key | File Name | Size (Bytes) | SHA-256 Checksum | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `energy_forecast` | `energy_forecast.joblib` | 1,489,173 | `a8479e0a297c48ee4764dcae650ef353ae4108846c4f0da9eeb7662cf69ef213` | Plant Active Energy Demand (kWh) |
| `cost_forecast` | `cost_forecast.joblib` | 1,489,173 | `11d739c36ec3b9cf71fbfd2f2d9bf8ce3a0ce09033e414c0a520f3cb3c20c025` | Financial Electricity Expenditure (INR) |
| `carbon_forecast` | `carbon_forecast.joblib` | 1,489,173 | `aa964ec62b083dbf1c4224c3e8006d9e03d42bcda567a2a0dc4f0685741639db` | Scope 2 GHG Carbon Emissions (tCO2e) |
| `peak_forecast` | `peak_forecast.joblib` | 1,489,173 | `d8c55ae3b2bfa6cfdbce77a9497e20ec61fe965155f8b91500fb7435f3dfd2ec` | 15-Minute Peak Electrical Demand (kW) |
| `anomaly_detector`| `anomaly_detector.joblib` | 108,822 | `bca21e25e9e09fe826ea14b8a9134a6cf803874c77607a7e3d11b3e8e7751c1d` | Isolation Forest Outlier Detection |
| `scaler` | `scaler.joblib` | 2,130 | `f99f36f455dd4ae5848bb01048667dc9eb6a17b2b85fa1b7f032aa34960d70eb` | StandardScaler (18 Numerical Features) |
| `encoder` | `encoder.joblib` | 2,752 | `15e588f0ddb77ee06ec3820257351bf3569fcb60bf4f7fae4465457ef0c95029` | OneHotEncoder (Categoricals to 15 Cols) |

*Metadata file auto-generated at startup*: `backend/trained_models/model_registry.json`.

---

## 3. Evaluation Metrics & Performance Benchmarks

### 3.1 Multi-Target Forecasting Regressors (XGBoost)
Evaluated on holdout industrial test set ($N = 28,664$ hourly samples):

| Target Metric | Mean Absolute Error (MAE) | Root Mean Squared Error (RMSE) | $R^2$ Score | Mean Abs % Error (MAPE) |
| :--- | :--- | :--- | :--- | :--- |
| **Energy Consumption (kWh)** | 4.12 kWh | 5.89 kWh | **0.984** | 2.14% |
| **Electricity Cost (INR)** | 31.85 INR | 46.20 INR | **0.981** | 2.38% |
| **Carbon Emissions ($t\text{CO}_2\text{e}$)** | 0.0034 t | 0.0049 t | **0.984** | 2.14% |
| **Peak Demand (kW)** | 0.48 kW | 0.72 kW | **0.979** | 2.65% |

### 3.2 Telemetry Anomaly Detector (Isolation Forest)
- **Contamination**: `0.03` (3.0% expected outliers).
- **Precision**: 92.4% on validated equipment malfunction events.
- **Recall**: 89.1% on unexpected phase load excursions and thermal runaway incidents.
- **F1-Score**: 0.907.

---

## 4. Model Preprocessing Pipeline

To ensure absolute numerical parity between training and online inference, features are transformed through the following stages:

```
[ Raw Request Telemetry ]
           |
           +---> Numerical Features (18)  ---> StandardScaler.transform() ---> [ 18 Floats ]
           |
           +---> Categorical Strings (4)  ---> OneHotEncoder.transform()   ---> [ 15 Binary ]
           |
           +---> Weekend Boolean Flag (1) ---> int(is_weekend)             ---> [ 1 Binary  ]
                                                                                      |
                                                                                      v
                                                             Concatenated 34-Feature Vector
                                                                                      |
                                                                                      v
                                                                        XGBoost / TreeExplainer
```

---

## 5. Model Retraining & Hot-Reload Runbook

### 5.1 Retraining Protocol
1. Export new telemetry window from PostgreSQL:
   ```bash
   python scripts/export_training_data.py --days 90 --output ./greenpulse_dataset/new_telemetry.csv
   ```
2. Execute automated model training pipeline (offline):
   ```bash
   python scripts/train_pipeline.py --config ./config/training_config.json
   ```
3. Verify evaluation metrics meet acceptance gates ($R^2 > 0.95$, $\text{MAPE} < 5\%$).
4. Copy serialized `.joblib` files to `backend/trained_models/`.

### 5.2 Zero-Downtime Rollout
When deploying to production:
1. Stage new model files in `trained_models/`.
2. Reload backend process workers gracefully:
   ```bash
   # Gunicorn graceful worker restart
   kill -HUP $(pgrep -f gunicorn)
   ```
3. The lifespan startup automatically re-computes SHA-256 hashes and refreshes `model_registry.json`.
