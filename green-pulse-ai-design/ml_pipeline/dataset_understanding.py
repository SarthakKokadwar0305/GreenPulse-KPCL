"""
GreenPulse AI - Step 1: Dataset Understanding & Metadata Extraction
Analyzes all raw and engineered CSV datasets, verifies schema fidelity, extracts statistical profiles,
and determines feasible industrial prediction targets without assuming nonexistent columns.
"""
import json
import logging
from pathlib import Path
from typing import Any, Dict, List
import pandas as pd
import numpy as np

from ml_pipeline.config import (
    DATASET_DIR,
    ALT_DATASET_DIR,
    RESULTS_DIR,
    INTERVAL_HOURS,
    BASE_TARIFF_INR_PER_KWH,
    PEAK_TARIFF_INR_PER_KWH,
    OFF_PEAK_TARIFF_INR_PER_KWH,
    GRID_EMISSION_FACTOR_KG_PER_KWH,
)

logger = logging.getLogger("GreenPulseML.DatasetUnderstanding")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


def get_dataset_path(filename: str) -> Path:
    """Finds dataset in primary or alternate dataset path."""
    primary = DATASET_DIR / filename
    if primary.exists():
        return primary
    alt = ALT_DATASET_DIR / filename
    if alt.exists():
        return alt
    raise FileNotFoundError(f"Could not locate dataset: {filename}")


def compute_tariff_series(hour_series: pd.Series) -> pd.Series:
    """Calculates Time-of-Day (ToD) tariff in INR/kWh based on hour of day."""
    peak_mask = hour_series.isin([10, 11, 18, 19, 20, 21])
    off_peak_mask = hour_series.isin([22, 23, 0, 1, 2, 3, 4, 5])
    
    tariffs = pd.Series(BASE_TARIFF_INR_PER_KWH, index=hour_series.index)
    tariffs[peak_mask] = PEAK_TARIFF_INR_PER_KWH
    tariffs[off_peak_mask] = OFF_PEAK_TARIFF_INR_PER_KWH
    return tariffs


def add_derived_targets(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes rigorous industrial target variables directly from raw active power readings:
    1. target_energy_kwh = target_power_next_interval_kw * (5 / 60)
    2. target_cost_inr = target_energy_kwh * ToD_tariff
    3. target_carbon_kg = target_energy_kwh * 0.82
    4. target_peak_kw = target_power_next_interval_kw
    5. load_ratio = power_kw / rated_power_kw
    """
    df = df.copy()
    
    # Load ratio
    if "rated_power_kw" in df.columns and "power_kw" in df.columns:
        df["load_ratio"] = np.clip(df["power_kw"] / np.maximum(df["rated_power_kw"], 1.0), 0.0, 1.5)
    
    # 1. Target Energy Consumption (kWh)
    if "target_power_next_interval_kw" in df.columns:
        df["target_energy_kwh"] = df["target_power_next_interval_kw"] * INTERVAL_HOURS
        df["target_peak_kw"] = df["target_power_next_interval_kw"]

        # 2. Target Cost (INR)
        tariff_rates = compute_tariff_series(df["hour"])
        df["target_cost_inr"] = df["target_energy_kwh"] * tariff_rates

        # 3. Target Carbon Emissions (kg CO2e)
        df["target_carbon_kg"] = df["target_energy_kwh"] * GRID_EMISSION_FACTOR_KG_PER_KWH

    return df


def analyze_single_dataset(file_path: Path) -> Dict[str, Any]:
    """Inspects columns, types, nulls, and statistics for a single dataset."""
    logger.info(f"Analyzing dataset: {file_path.name}")
    df = pd.read_csv(file_path)
    
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    bool_cols = df.select_dtypes(include=["bool"]).columns.tolist()
    
    null_counts = df.isnull().sum().to_dict()
    
    col_summary = {}
    for col in df.columns:
        dtype_str = str(df[col].dtype)
        unique_vals = int(df[col].nunique())
        col_summary[col] = {
            "dtype": dtype_str,
            "null_count": int(null_counts.get(col, 0)),
            "null_percentage": round(float(null_counts.get(col, 0) / len(df) * 100), 2),
            "unique_count": unique_vals,
            "sample_values": df[col].dropna().head(3).tolist(),
        }
        if col in num_cols:
            col_summary[col]["min"] = float(round(df[col].min(), 4))
            col_summary[col]["max"] = float(round(df[col].max(), 4))
            col_summary[col]["mean"] = float(round(df[col].mean(), 4))
            col_summary[col]["std"] = float(round(df[col].std(), 4))

    return {
        "filename": file_path.name,
        "rows": len(df),
        "columns_count": len(df.columns),
        "columns": df.columns.tolist(),
        "numerical_columns": num_cols,
        "categorical_columns": cat_cols,
        "boolean_columns": bool_cols,
        "column_details": col_summary,
    }


def run_dataset_understanding() -> Dict[str, Any]:
    """Executes Step 1 for all project datasets and writes dataset_summary.json."""
    logger.info("Starting Step 1: Comprehensive Industrial Dataset Understanding...")
    
    dataset_files = [
        "ml_train.csv",
        "ml_validation.csv",
        "ml_test.csv",
        "ml_features_all.csv",
        "machine_energy_summary.csv",
        "daily_energy_by_machine.csv",
        "hourly_pattern_by_machine.csv",
        "production_efficiency_by_day.csv",
    ]
    
    summaries = {}
    for fname in dataset_files:
        try:
            fpath = get_dataset_path(fname)
            summaries[fname] = analyze_single_dataset(fpath)
        except Exception as e:
            logger.warning(f"Could not analyze {fname}: {e}")

    # Domain Classification from ml_train.csv
    train_summary = summaries.get("ml_train.csv", {})
    all_train_cols = train_summary.get("columns", [])
    
    domain_mapping = {
        "time_series_columns": [c for c in all_train_cols if any(k in c for k in ["timestamp", "hour", "day_of_week", "sin", "cos"])],
        "machine_identifiers": [c for c in all_train_cols if "machine_id" in c],
        "machine_operational_state": [c for c in all_train_cols if any(k in c for k in ["state", "shift", "ambient_temp", "rated"])],
        "energy_power_telemetry": [c for c in all_train_cols if any(k in c for k in ["power", "energy", "lag", "rolling"])],
        "supported_forecasting_targets": [
            "target_energy_kwh (Active electrical consumption per 5-min interval)",
            "target_cost_inr (Operational expenditure under ToD peak/off-peak tariffs)",
            "target_carbon_kg (Scope 2 GHG emissions at 0.82 kg/kWh)",
            "target_peak_kw (Interval peak demand in kW for MDI tracking)",
        ],
        "supported_anomaly_tasks": [
            "Unsupervised equipment state autoencoder/isolation forest based on power, lag dynamics, temperature, and load ratio."
        ],
    }

    full_report = {
        "title": "GreenPulse AI - Industrial Dataset Understanding Summary",
        "total_datasets_analyzed": len(summaries),
        "domain_variable_classification": domain_mapping,
        "dataset_profiles": summaries,
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    summary_path = RESULTS_DIR / "dataset_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(full_report, f, indent=2)

    logger.info(f"Step 1 Complete: Dataset summary written to {summary_path}")
    return full_report


if __name__ == "__main__":
    run_dataset_understanding()
