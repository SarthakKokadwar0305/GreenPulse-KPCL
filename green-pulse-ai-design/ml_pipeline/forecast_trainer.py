"""
GreenPulse AI - Step 4: Forecasting Models Training & Tuning
Trains production XGBoost models for:
1. Energy Consumption (kWh) -> energy_forecast.joblib
2. Electricity Cost (INR) -> cost_forecast.joblib
3. Carbon Emissions (kg CO2e) -> carbon_forecast.joblib
4. Peak Demand (kW) -> peak_forecast.joblib

Performs hyperparameter tuning, cross-validation, and saves artifacts with metadata.
"""
import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.model_selection import RandomizedSearchCV, TimeSeriesSplit
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor

from ml_pipeline.config import (
    TRAINED_MODELS_DIR,
    BACKEND_MODELS_DIR,
    RESULTS_DIR,
    PREDICTION_PLOTS_DIR,
    RESIDUAL_PLOTS_DIR,
    RANDOM_STATE,
    CATEGORICAL_FEATURES,
    BOOLEAN_FEATURES,
    NUMERICAL_FEATURES,
    TARGET_ENERGY,
    TARGET_COST,
    TARGET_CARBON,
    TARGET_PEAK,
    XGB_PARAM_GRID,
)
from ml_pipeline.dataset_understanding import get_dataset_path, add_derived_targets
from ml_pipeline.model_selection import calculate_mape

logger = logging.getLogger("GreenPulseML.ForecastTrainer")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


class IndustrialDataPipeline:
    """Production preprocessor that fits one-hot encoders and scalers strictly on train data."""
    def __init__(self):
        self.encoder = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
        self.scaler = StandardScaler()
        self.feature_names: List[str] = []
        self.num_cols: List[str] = []
        self.cat_cols: List[str] = []

    def fit(self, df: pd.DataFrame) -> "IndustrialDataPipeline":
        self.num_cols = [c for c in NUMERICAL_FEATURES if c in df.columns]
        self.cat_cols = [c for c in CATEGORICAL_FEATURES if c in df.columns]

        # Fit encoder on categoricals
        self.encoder.fit(df[self.cat_cols])
        encoded_cat_names = self.encoder.get_feature_names_out(self.cat_cols).tolist()

        # Fit scaler on numericals
        self.scaler.fit(df[self.num_cols])

        # Combined feature list
        self.feature_names = self.num_cols + BOOLEAN_FEATURES + encoded_cat_names
        return self

    def transform(self, df: pd.DataFrame) -> np.ndarray:
        # Scale numericals
        num_scaled = self.scaler.transform(df[self.num_cols])
        # Encode categoricals
        cat_encoded = self.encoder.transform(df[self.cat_cols])
        # Booleans
        bool_vals = df[BOOLEAN_FEATURES].astype(float).values

        return np.hstack([num_scaled, bool_vals, cat_encoded])


def tune_xgboost_hyperparameters(X_train: np.ndarray, y_train: np.ndarray) -> Dict[str, Any]:
    """Runs RandomizedSearchCV with TimeSeriesSplit to discover optimal hyperparameters."""
    logger.info("Executing RandomizedSearchCV for XGBoost hyperparameter tuning...")
    base_xgb = XGBRegressor(
        tree_method="hist",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    
    cv = TimeSeriesSplit(n_splits=3)
    search = RandomizedSearchCV(
        estimator=base_xgb,
        param_distributions=XGB_PARAM_GRID,
        n_iter=6,
        scoring="neg_mean_absolute_error",
        cv=cv,
        random_state=RANDOM_STATE,
        verbose=1,
        n_jobs=1,
    )
    
    # Subsample for tuning efficiency
    sub_indices = np.random.RandomState(RANDOM_STATE).choice(len(X_train), size=min(25000, len(X_train)), replace=False)
    search.fit(X_train[sub_indices], y_train[sub_indices])
    
    logger.info(f"Optimal hyperparameters: {search.best_params_}")
    return search.best_params_


def plot_predictions(y_true: np.ndarray, y_pred: np.ndarray, title: str, save_path: Path, unit: str = ""):
    """Generates scatter plot of Actual vs Predicted with ideal reference line."""
    plt.figure(figsize=(9, 7))
    sample_size = min(3000, len(y_true))
    idx = np.random.RandomState(RANDOM_STATE).choice(len(y_true), size=sample_size, replace=False)
    
    plt.scatter(y_true[idx], y_pred[idx], alpha=0.35, edgecolors="none", color="#10B981", s=18)
    
    min_val = min(y_true[idx].min(), y_pred[idx].min())
    max_val = max(y_true[idx].max(), y_pred[idx].max())
    plt.plot([min_val, max_val], [min_val, max_val], color="#EF4444", linestyle="--", linewidth=2, label="Ideal Fit (y = x)")
    
    r2 = r2_score(y_true, y_pred)
    mae = mean_absolute_error(y_true, y_pred)
    
    plt.title(f"{title} (Actual vs Predicted)\nR²: {r2:.4f} | MAE: {mae:.4f} {unit}", fontsize=12, pad=12)
    plt.xlabel(f"Actual Measured {unit}", fontsize=11)
    plt.ylabel(f"Model Predicted {unit}", fontsize=11)
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(save_path, dpi=160)
    plt.close()


def plot_residuals(y_true: np.ndarray, y_pred: np.ndarray, title: str, save_path: Path, unit: str = ""):
    """Generates residual diagnostics plot (Residuals vs Predicted + Error Distribution)."""
    residuals = y_true - y_pred
    sample_size = min(3000, len(y_true))
    idx = np.random.RandomState(RANDOM_STATE).choice(len(y_true), size=sample_size, replace=False)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Residuals vs Predicted
    ax1.scatter(y_pred[idx], residuals[idx], alpha=0.35, color="#0EA5E9", s=18)
    ax1.axhline(0, color="#EF4444", linestyle="--", linewidth=1.5)
    ax1.set_title(f"{title} - Residuals vs Predicted", fontsize=11)
    ax1.set_xlabel(f"Predicted Value {unit}", fontsize=10)
    ax1.set_ylabel(f"Residual (Actual - Pred) {unit}", fontsize=10)
    ax1.grid(alpha=0.3)
    
    # Error distribution histogram
    ax2.hist(residuals, bins=50, color="#6366F1", alpha=0.75, edgecolor="white")
    ax2.axvline(0, color="#EF4444", linestyle="--", linewidth=1.5)
    ax2.set_title(f"{title} - Residual Distribution\nMean: {np.mean(residuals):.4f} | Std: {np.std(residuals):.4f}", fontsize=11)
    ax2.set_xlabel(f"Residual Error {unit}", fontsize=10)
    ax2.set_ylabel("Frequency", fontsize=10)
    ax2.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=160)
    plt.close()


def train_forecasting_models() -> Dict[str, Any]:
    """Trains, tunes, evaluates, and saves the 4 industrial forecasting models."""
    logger.info("Loading training, validation, and test datasets...")
    train_df = add_derived_targets(pd.read_csv(get_dataset_path("ml_train.csv")))
    val_df = add_derived_targets(pd.read_csv(get_dataset_path("ml_validation.csv")))
    test_df = add_derived_targets(pd.read_csv(get_dataset_path("ml_test.csv")))

    # Fit industrial preprocessing pipeline
    logger.info("Fitting preprocessing pipeline on training partition only...")
    pipeline = IndustrialDataPipeline()
    pipeline.fit(train_df)

    X_train = pipeline.transform(train_df)
    X_val = pipeline.transform(val_df)
    X_test = pipeline.transform(test_df)

    # Save Preprocessor Artifacts
    TRAINED_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    BACKEND_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    PREDICTION_PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    RESIDUAL_PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    joblib.dump(pipeline.scaler, TRAINED_MODELS_DIR / "scaler.joblib")
    joblib.dump(pipeline.scaler, BACKEND_MODELS_DIR / "scaler.joblib")
    joblib.dump(pipeline.encoder, TRAINED_MODELS_DIR / "encoder.joblib")
    joblib.dump(pipeline.encoder, BACKEND_MODELS_DIR / "encoder.joblib")

    with open(TRAINED_MODELS_DIR / "feature_list.json", "w") as f:
        json.dump(pipeline.feature_names, f, indent=2)
    with open(BACKEND_MODELS_DIR / "feature_list.json", "w") as f:
        json.dump(pipeline.feature_names, f, indent=2)

    # Hyperparameter search on Energy Target
    tuned_params = tune_xgboost_hyperparameters(X_train, train_df[TARGET_ENERGY].values)
    
    # Save training configuration
    train_config = {
        "random_state": RANDOM_STATE,
        "n_features": len(pipeline.feature_names),
        "feature_names": pipeline.feature_names,
        "train_rows": len(train_df),
        "val_rows": len(val_df),
        "test_rows": len(test_df),
        "tuned_hyperparameters": tuned_params,
        "algorithm": "XGBoost Regressor (Histogram Gradient Boosting)",
    }
    with open(TRAINED_MODELS_DIR / "training_config.json", "w") as f:
        json.dump(train_config, f, indent=2)

    # Task Specifications
    tasks = [
        {
            "name": "Energy Consumption",
            "target_col": TARGET_ENERGY,
            "filename": "energy_forecast.joblib",
            "unit": "kWh",
            "description": "5-minute active electrical consumption trajectory"
        },
        {
            "name": "Electricity Cost",
            "target_col": TARGET_COST,
            "filename": "cost_forecast.joblib",
            "unit": "INR",
            "description": "Financial expenditure with Time-of-Day ToD tariffs"
        },
        {
            "name": "Carbon Emissions",
            "target_col": TARGET_CARBON,
            "filename": "carbon_forecast.joblib",
            "unit": "kg CO2e",
            "description": "Scope 2 GHG emissions (0.82 kg CO2e / kWh factor)"
        },
        {
            "name": "Peak Demand",
            "target_col": TARGET_PEAK,
            "filename": "peak_forecast.joblib",
            "unit": "kW",
            "description": "Next-interval peak load demand for MDI tracking"
        },
    ]

    model_metrics = {}
    
    for task in tasks:
        target_name = task["name"]
        target_col = task["target_col"]
        joblib_name = task["filename"]
        unit = task["unit"]
        
        logger.info(f"Training production XGBoost model for: {target_name} ({target_col})...")
        y_train = train_df[target_col].values
        y_val = val_df[target_col].values
        y_test = test_df[target_col].values

        model = XGBRegressor(
            **tuned_params,
            tree_method="hist",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        )

        t0 = time.perf_counter()
        model.fit(
            X_train,
            y_train,
            eval_set=[(X_val, y_val)],
            verbose=False,
        )
        training_time = time.perf_counter() - t0

        # Predictions
        train_preds = model.predict(X_train)
        val_preds = model.predict(X_val)
        test_preds = model.predict(X_test)

        # Metrics Evaluation
        metrics = {
            "task": target_name,
            "target_column": target_col,
            "unit": unit,
            "training_time_seconds": round(float(training_time), 2),
            "train": {
                "r2": round(float(r2_score(y_train, train_preds)), 4),
                "mae": round(float(mean_absolute_error(y_train, train_preds)), 4),
                "rmse": round(float(np.sqrt(mean_squared_error(y_train, train_preds))), 4),
                "mape_pct": round(float(calculate_mape(y_train, train_preds)), 2),
            },
            "validation": {
                "r2": round(float(r2_score(y_val, val_preds)), 4),
                "mae": round(float(mean_absolute_error(y_val, val_preds)), 4),
                "rmse": round(float(np.sqrt(mean_squared_error(y_val, val_preds))), 4),
                "mape_pct": round(float(calculate_mape(y_val, val_preds)), 2),
            },
            "test": {
                "r2": round(float(r2_score(y_test, test_preds)), 4),
                "mae": round(float(mean_absolute_error(y_test, test_preds)), 4),
                "rmse": round(float(np.sqrt(mean_squared_error(y_test, test_preds))), 4),
                "mape_pct": round(float(calculate_mape(y_test, test_preds)), 2),
            },
        }

        # Check generalization gap (Overfitting check)
        r2_gap = metrics["train"]["r2"] - metrics["test"]["r2"]
        metrics["generalization_status"] = "Well Generalized" if r2_gap < 0.05 else "Moderate Variance"
        metrics["overfitting_gap_r2"] = round(float(r2_gap), 4)

        logger.info(
            f"[{target_name}] Test R²: {metrics['test']['r2']} | Test MAE: {metrics['test']['mae']} {unit} | Test MAPE: {metrics['test']['mape_pct']}%"
        )

        # Save Joblib Models
        save_path_root = TRAINED_MODELS_DIR / joblib_name
        save_path_backend = BACKEND_MODELS_DIR / joblib_name
        joblib.dump(model, save_path_root)
        joblib.dump(model, save_path_backend)
        logger.info(f"Saved model artifact: {save_path_root} and {save_path_backend}")

        # Diagnostic Plots
        safe_prefix = target_name.lower().replace(" ", "_")
        plot_predictions(
            y_test, test_preds,
            title=f"{target_name} Prediction",
            save_path=PREDICTION_PLOTS_DIR / f"{safe_prefix}_pred_vs_actual.png",
            unit=unit
        )
        plot_residuals(
            y_test, test_preds,
            title=f"{target_name} Residuals",
            save_path=RESIDUAL_PLOTS_DIR / f"{safe_prefix}_residuals.png",
            unit=unit
        )

        model_metrics[target_col] = metrics

    # Save Model Metadata
    metadata = {
        "model_architecture": "XGBoost Histogram Regressor",
        "training_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "random_state": RANDOM_STATE,
        "input_features_count": len(pipeline.feature_names),
        "target_metrics": model_metrics,
    }
    with open(TRAINED_MODELS_DIR / "model_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    with open(BACKEND_MODELS_DIR / "model_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    return model_metrics


if __name__ == "__main__":
    train_forecasting_models()
