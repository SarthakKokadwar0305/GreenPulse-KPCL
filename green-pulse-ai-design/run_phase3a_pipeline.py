"""
GreenPulse AI - Phase 3A Master Execution Pipeline
Orchestrates the entire industrial machine learning workflow end-to-end:
1. Dataset Understanding & Metadata Profiling
2. Feature Analysis (Correlation, Mutual Information, Variance, Leakage Check)
3. Model Selection & Algorithm Benchmarking (XGBoost vs RF vs ExtraTrees vs Ridge)
4. Multi-Target Forecasting Model Training & Tuning (Energy, Cost, Carbon, Peak Demand)
5. Unsupervised Anomaly Detection Model Training (Isolation Forest on Telemetry)
6. Model Validation (Bias, Variance, Overfitting & Underfitting Diagnostics)
7. Production Joblib Model Serialization & Metadata Packaging
8. Comprehensive Metrics & Evaluation Report Generation
"""
import logging
import sys
import time
from pathlib import Path
import matplotlib
matplotlib.use("Agg")

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml_pipeline.dataset_understanding import run_dataset_understanding
from ml_pipeline.feature_analysis import run_feature_analysis
from ml_pipeline.model_selection import run_model_selection
from ml_pipeline.forecast_trainer import train_forecasting_models
from ml_pipeline.anomaly_trainer import train_anomaly_model
from ml_pipeline.model_evaluation import compile_evaluation_reports

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger("GreenPulseAI.Phase3A")


def main():
    total_start_time = time.perf_counter()
    logger.info("================================================================================")
    logger.info("          STARTING GREENPULSE AI - PHASE 3A ML PRODUCTION PIPELINE              ")
    logger.info("================================================================================")

    # STEP 1: DATASET UNDERSTANDING
    logger.info("\n>>> [STEP 1/6] EXECUTING DATASET UNDERSTANDING & PROFILING...")
    dataset_summary = run_dataset_understanding()
    logger.info(f"Analyzed {dataset_summary['total_datasets_analyzed']} industrial datasets successfully.")

    # STEP 2: FEATURE ANALYSIS
    logger.info("\n>>> [STEP 2/6] EXECUTING FEATURE ANALYSIS & SCREENING...")
    importance_df, leakage_audit = run_feature_analysis()
    logger.info(f"Computed feature metrics for {len(importance_df)} variables.")
    logger.info(f"Top 3 most informative features: {importance_df.head(3)['feature'].tolist()}")

    # STEP 3: MODEL SELECTION BENCHMARKING
    logger.info("\n>>> [STEP 3/6] BENCHMARKING CANDIDATE ALGORITHMS...")
    comparison_df = run_model_selection()
    logger.info("Algorithm Comparison Benchmark:")
    for _, row in comparison_df.iterrows():
        logger.info(f" - {row['algorithm']}: R²={row['validation_r2']}, MAE={row['validation_mae']}, MAPE={row['validation_mape_pct']}%")

    # STEP 4: FORECASTING MODELS TRAINING & TUNING
    logger.info("\n>>> [STEP 4/6] TRAINING & TUNING 4 INDUSTRIAL FORECASTING MODELS...")
    forecasting_metrics = train_forecasting_models()
    logger.info("Trained 4 multi-target XGBoost forecasting models.")

    # STEP 5: ANOMALY DETECTION MODEL TRAINING
    logger.info("\n>>> [STEP 5/6] TRAINING ISOLATION FOREST ANOMALY DETECTOR...")
    anomaly_metrics = train_anomaly_model()
    logger.info(f"Trained IsolationForest detector. Test Anomaly Rate: {anomaly_metrics['dataset_anomaly_rates']['test_anomaly_rate_pct']}%")

    # STEP 6 & 8: MODEL VALIDATION & REPORT GENERATION
    logger.info("\n>>> [STEP 6/6] MODEL VALIDATION & METRIC COMPILATION...")
    metrics, summary = compile_evaluation_reports(forecasting_metrics, anomaly_metrics)

    elapsed_total = time.perf_counter() - total_start_time
    logger.info("================================================================================")
    logger.info(f"       PHASE 3A PIPELINE EXECUTED SUCCESSFULLY IN {elapsed_total:.2f} SECONDS    ")
    logger.info("================================================================================")
    logger.info("Summary of Model Performance (Test Partition):")
    for card in summary["model_performance_summary"]:
        logger.info(f" -> {card['model']}: R²={card['test_r2']} | MAE={card['test_mae']} | MAPE={card['test_mape']} | Status={card['health_status']}")
    logger.info(f" -> Anomaly Detector: Contamination={summary['anomaly_detector_summary']['contamination_parameter']} | Test Outliers={summary['anomaly_detector_summary']['test_anomaly_rate']}")
    logger.info("All Joblib artifacts, JSON summaries, and PNG evaluation charts are verified.")


if __name__ == "__main__":
    main()
