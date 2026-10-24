"""
GreenPulse AI - ML Pipeline Configuration
Enterprise MLOps configuration containing feature definitions, random seeds, paths, and hyperparameters.
"""
import matplotlib
matplotlib.use("Agg")
from pathlib import Path

# Base Paths
ROOT_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = ROOT_DIR / "backend" / "datasets"
ALT_DATASET_DIR = ROOT_DIR.parent / "greenpulse_dataset" / "eda_output"
TRAINED_MODELS_DIR = ROOT_DIR / "trained_models"
BACKEND_MODELS_DIR = ROOT_DIR / "backend" / "trained_models"
RESULTS_DIR = ROOT_DIR / "results"
PREDICTION_PLOTS_DIR = RESULTS_DIR / "prediction_plots"
RESIDUAL_PLOTS_DIR = RESULTS_DIR / "residual_plots"
CONFUSION_DIR = RESULTS_DIR / "confusion_analysis"

# Global Random State
RANDOM_STATE = 42

# Industrial Operational Constants
GRID_EMISSION_FACTOR_KG_PER_KWH = 0.82
BASE_TARIFF_INR_PER_KWH = 7.20
PEAK_TARIFF_INR_PER_KWH = 10.368  # 7.20 * 1.44 (Hours 10-12, 18-22)
OFF_PEAK_TARIFF_INR_PER_KWH = 5.20  # Night hours (22-06)
INTERVAL_HOURS = 5.0 / 60.0  # 5-minute sampling interval = 1/12 hour

# Feature Definitions
CATEGORICAL_FEATURES = ["machine_id", "machine_state", "shift"]
BOOLEAN_FEATURES = ["is_weekend"]

NUMERICAL_FEATURES = [
    "rated_power_kw",
    "ambient_temp_c",
    "power_kw",
    "energy_kwh",
    "power_lag_1",
    "power_lag_2",
    "power_lag_3",
    "power_lag_6",
    "power_lag_12",
    "power_lag_288",
    "power_lag_2016",
    "rolling_mean_1h",
    "rolling_std_1h",
    "hour_sin",
    "hour_cos",
    "dow_sin",
    "dow_cos",
    "load_ratio",
]

# Operational Telemetry Features for Anomaly Detection
ANOMALY_FEATURE_COLS = [
    "power_kw",
    "rated_power_kw",
    "ambient_temp_c",
    "rolling_mean_1h",
    "rolling_std_1h",
    "power_lag_1",
    "power_lag_2",
    "power_lag_3",
    "load_ratio",
]

# Prediction Target Names
TARGET_ENERGY = "target_energy_kwh"
TARGET_COST = "target_cost_inr"
TARGET_CARBON = "target_carbon_kg"
TARGET_PEAK = "target_peak_kw"

ALL_TARGETS = [TARGET_ENERGY, TARGET_COST, TARGET_CARBON, TARGET_PEAK]

# Hyperparameter Search Spaces
XGB_PARAM_GRID = {
    "n_estimators": [100, 150, 200],
    "max_depth": [4, 6, 8],
    "learning_rate": [0.03, 0.05, 0.1],
    "subsample": [0.8, 1.0],
    "colsample_bytree": [0.8, 1.0],
}

ISOLATION_FOREST_PARAMS = {
    "n_estimators": 150,
    "contamination": 0.035,  # Matches ~3.5% injected anomaly prevalence
    "max_samples": 0.8,
    "random_state": RANDOM_STATE,
    "n_jobs": -1,
}
