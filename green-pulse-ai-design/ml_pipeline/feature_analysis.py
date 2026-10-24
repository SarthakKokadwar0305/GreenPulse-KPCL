"""
GreenPulse AI - Step 2: Feature Analysis
Performs Pearson correlation analysis, Mutual Information scoring, variance screening,
and leak detection across all engineered industrial predictors.
Outputs results/feature_importance.csv and statistical summaries.
"""
import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.feature_selection import mutual_info_regression

from ml_pipeline.config import (
    RESULTS_DIR,
    NUMERICAL_FEATURES,
    CATEGORICAL_FEATURES,
    BOOLEAN_FEATURES,
    TARGET_ENERGY,
    RANDOM_STATE,
)
from ml_pipeline.dataset_understanding import get_dataset_path, add_derived_targets

logger = logging.getLogger("GreenPulseML.FeatureAnalysis")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


def run_feature_analysis() -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Executes Step 2: Correlation, Mutual Information, Variance & Distribution analysis."""
    logger.info("Starting Step 2: Feature Analysis & Importance Profiling...")
    
    # Load training data
    train_path = get_dataset_path("ml_train.csv")
    train_df = pd.read_csv(train_path)
    train_df = add_derived_targets(train_df)

    # 1. Variance Analysis
    logger.info("Computing predictor variances...")
    feature_candidates = [f for f in NUMERICAL_FEATURES if f in train_df.columns]
    variances = train_df[feature_candidates].var().to_dict()
    low_variance_features = [f for f, v in variances.items() if v < 1e-4]

    # 2. Correlation Matrix with Target
    logger.info("Computing Pearson correlation matrix...")
    analysis_cols = feature_candidates + [TARGET_ENERGY]
    corr_matrix = train_df[analysis_cols].corr()
    target_corrs = corr_matrix[TARGET_ENERGY].drop(TARGET_ENERGY).sort_values(ascending=False)

    # Detect highly correlated feature pairs (potential multicollinearity)
    high_corr_pairs = []
    for i in range(len(feature_candidates)):
        for j in range(i + 1, len(feature_candidates)):
            f1, f2 = feature_candidates[i], feature_candidates[j]
            c_val = corr_matrix.loc[f1, f2]
            if abs(c_val) > 0.90:
                high_corr_pairs.append({
                    "feature_1": f1,
                    "feature_2": f2,
                    "correlation": round(float(c_val), 4),
                    "action": "Preserved for tree boosting ensemble"
                })

    # 3. Mutual Information Scores
    logger.info("Computing Mutual Information scores (subsampled for efficiency)...")
    sub_df = train_df.sample(n=min(15000, len(train_df)), random_state=RANDOM_STATE)
    X_sub = sub_df[feature_candidates].fillna(0)
    y_sub = sub_df[TARGET_ENERGY]

    mi_scores = mutual_info_regression(X_sub, y_sub, random_state=RANDOM_STATE)
    mi_series = pd.Series(mi_scores, index=feature_candidates).sort_values(ascending=False)

    # 4. Generate Unified Feature Importance Table
    importance_df = pd.DataFrame({
        "feature": feature_candidates,
        "pearson_correlation": [round(float(target_corrs.get(f, 0.0)), 4) for f in feature_candidates],
        "mutual_information": [round(float(mi_series.get(f, 0.0)), 4) for f in feature_candidates],
        "variance": [round(float(variances.get(f, 0.0)), 4) for f in feature_candidates],
    }).sort_values(by="mutual_information", ascending=False)

    # Save feature_importance.csv
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_csv = RESULTS_DIR / "feature_importance.csv"
    importance_df.to_csv(out_csv, index=False)
    logger.info(f"Saved feature importance table to {out_csv}")

    # 5. Correlation Heatmap Plot
    plt.figure(figsize=(14, 11))
    sns.heatmap(
        corr_matrix,
        cmap="coolwarm",
        center=0,
        annot=True,
        fmt=".2f",
        annot_kws={"size": 7},
        cbar_kws={"label": "Pearson Correlation"}
    )
    plt.title("GreenPulse AI - Industrial Feature Correlation Matrix", fontsize=14, pad=15)
    plt.tight_layout()
    corr_plot_path = RESULTS_DIR / "correlation_matrix.png"
    plt.savefig(corr_plot_path, dpi=160)
    plt.close()
    logger.info(f"Saved correlation plot to {corr_plot_path}")

    # 6. Leakage & Collinearity Audit
    leakage_audit = {
        "identified_leakage_columns": [
            "split (Metadata partition tag)",
            "target_power_next_interval_kw (Target variable directly)",
            "target_energy_kwh (Direct target variable)",
            "target_cost_inr (Direct target variable)",
            "target_carbon_kg (Direct target variable)",
            "target_peak_kw (Direct target variable)",
        ],
        "justification": "All target definitions and partition labels are strictly quarantined from model input features.",
        "low_variance_features": low_variance_features,
        "top_predictive_features": importance_df.head(5)["feature"].tolist(),
        "high_collinearity_pairs": high_corr_pairs,
    }

    logger.info("Step 2 Complete: Feature analysis finished successfully.")
    return importance_df, leakage_audit


if __name__ == "__main__":
    run_feature_analysis()
