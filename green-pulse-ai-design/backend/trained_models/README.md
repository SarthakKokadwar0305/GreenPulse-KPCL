# GreenPulse AI - Model Artifacts Directory (Phase 2)

This directory is designated for serializing and storing trained machine learning model artifacts (`.joblib`, `.onnx`, `.pt`).

## Model Contract Specifications

### 1. Multi-Horizon Forecasting Model
- **Filename**: `forecasting_tft_model.joblib` or `forecasting_xgb_model.joblib`
- **Loaded By**: `app/ml/model_loader.py` via `load_forecasting_model()`
- **Input Dimensions**: 24h lag window of power demand (kW), ambient temperature (°C), shift schedule encoding, solar irradiance (W/m²).
- **Target**: Next 24-168 hours active power trajectory with 80% and 95% quantile bounds.

### 2. Autoencoder Anomaly Detection Model
- **Filename**: `anomaly_autoencoder.joblib` or `anomaly_isolation_forest.joblib`
- **Loaded By**: `app/ml/model_loader.py` via `load_anomaly_model()`
- **Input Dimensions**: 3-phase currents ($I_a, I_b, I_c$), voltages ($V_{ab}, V_{bc}, V_{ca}$), power factor, frequency, winding temperature, vibration RMS.
- **Output**: Reconstruction loss / anomaly score $\in [0.0, 1.0]$ and individual feature z-score contributions.

## Current Phase (Phase 1 Baseline)
In Phase 1, `app.ml.model_loader` automatically binds the singleton `ModelArtifactRegistry` to resilient baseline estimators that conform 100% to the production API schema. When trained weights are dropped into this directory during Phase 2, `load_models()` will seamlessly switch from mock to native serialized inference without changing any API contract.
