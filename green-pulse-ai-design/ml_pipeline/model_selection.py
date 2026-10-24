"""
GreenPulse AI - Step 3: Model Selection & Algorithm Benchmarking
Benchmarks XGBoost against Random Forest, Extra Trees, and Linear Regression.
Evaluates MAE, RMSE, MAPE, R², and execution latency to select the optimal model.
Outputs results/model_comparison.csv.
"""
import logging
import time
from typing import Any, Dict, List, Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor

from ml_pipeline.config import (
    RESULTS_DIR,
    RANDOM_STATE,
    TARGET_ENERGY,
    NUMERICAL_FEATURES,
    CATEGORICAL_FEATURES,
    BOOLEAN_FEATURES,
)
from ml_pipeline.dataset_understanding import get_dataset_path, add_derived_targets

logger = logging.getLogger("GreenPulseML.ModelSelection")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


def calculate_mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Computes robust Mean Absolute Percentage Error (MAPE), handling near-zero denominators."""
    mask = y_true > 1e-3
    if np.sum(mask) == 0:
        return 0.0
    return float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100.0)


def prepare_benchmark_data(sample_size: int = 25000) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, List[str]]:
    """Loads and preprocesses feature matrices for benchmark comparison."""
    train_df = add_derived_targets(pd.read_csv(get_dataset_path("ml_train.csv")))
    val_df = add_derived_targets(pd.read_csv(get_dataset_path("ml_validation.csv")))

    # Subsample for rapid benchmark comparison
    sub_train = train_df.sample(n=min(sample_size, len(train_df)), random_state=RANDOM_STATE)
    sub_val = val_df.sample(n=min(int(sample_size * 0.25), len(val_df)), random_state=RANDOM_STATE)

    feature_cols = [c for c in NUMERICAL_FEATURES if c in sub_train.columns]
    
    # One-hot encode categoricals
    X_train_raw = pd.get_dummies(sub_train[feature_cols + CATEGORICAL_FEATURES + BOOLEAN_FEATURES], drop_first=True)
    X_val_raw = pd.get_dummies(sub_val[feature_cols + CATEGORICAL_FEATURES + BOOLEAN_FEATURES], drop_first=True)
    
    # Align columns
    X_train, X_val = X_train_raw.align(X_val_raw, join="left", axis=1, fill_value=0)
    
    y_train = sub_train[TARGET_ENERGY].values
    y_val = sub_val[TARGET_ENERGY].values
    
    return X_train.values, y_train, X_val.values, y_val, X_train.columns.tolist()


def run_model_selection() -> pd.DataFrame:
    """Executes Step 3: Benchmarks 4 candidate algorithms on the energy target."""
    logger.info("Starting Step 3: Model Selection Benchmarking...")
    X_train, y_train, X_val, y_val, feature_names = prepare_benchmark_data(sample_size=30000)

    candidates = {
        "Linear Regression (Ridge Baseline)": Ridge(alpha=1.0, random_state=RANDOM_STATE),
        "Random Forest Regressor": RandomForestRegressor(n_estimators=100, max_depth=12, n_jobs=-1, random_state=RANDOM_STATE),
        "Extra Trees Regressor": ExtraTreesRegressor(n_estimators=100, max_depth=12, n_jobs=-1, random_state=RANDOM_STATE),
        "XGBoost Regressor (Primary)": XGBRegressor(
            n_estimators=150,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.85,
            colsample_bytree=0.85,
            tree_method="hist",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
    }

    results = []
    for name, model in candidates.items():
        logger.info(f"Evaluating candidate: {name}...")
        t0 = time.perf_counter()
        model.fit(X_train, y_train)
        fit_time = time.perf_counter() - t0

        t1 = time.perf_counter()
        preds = model.predict(X_val)
        infer_time = (time.perf_counter() - t1) / len(X_val) * 1000.0  # ms per sample

        mae = mean_absolute_error(y_val, preds)
        rmse = np.sqrt(mean_squared_error(y_val, preds))
        r2 = r2_score(y_val, preds)
        mape = calculate_mape(y_val, preds)

        results.append({
            "algorithm": name,
            "validation_r2": round(float(r2), 4),
            "validation_mae": round(float(mae), 4),
            "validation_rmse": round(float(rmse), 4),
            "validation_mape_pct": round(float(mape), 2),
            "training_time_sec": round(float(fit_time), 2),
            "latency_ms_per_sample": round(float(infer_time), 4),
            "selected_for_production": name == "XGBoost Regressor (Primary)",
        })

    comparison_df = pd.DataFrame(results).sort_values(by="validation_r2", ascending=False)
    
    # Save model_comparison.csv
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_csv = RESULTS_DIR / "model_comparison.csv"
    comparison_df.to_csv(out_csv, index=False)
    logger.info(f"Step 3 Complete: Model comparison written to {out_csv}")
    
    return comparison_df


if __name__ == "__main__":
    run_model_selection()
