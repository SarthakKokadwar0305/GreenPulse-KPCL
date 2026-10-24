"""
GreenPulse AI - ML Services Package
Exports interfaces for forecasting, anomaly detection, recommendations, and simulations.
"""
from app.ml.model_loader import (
    load_models,
    load_forecasting_model,
    load_anomaly_model,
)
from app.ml.forecasting import (
    predict_energy,
    predict_cost,
    predict_carbon,
)
from app.ml.anomaly_detection import (
    detect_anomaly,
    calculate_risk_score,
)
from app.ml.recommendation_engine import (
    generate_recommendations,
    estimate_savings,
    estimate_roi,
)
from app.ml.simulator import (
    simulate,
    compare_scenarios,
)

__all__ = [
    "load_models",
    "load_forecasting_model",
    "load_anomaly_model",
    "predict_energy",
    "predict_cost",
    "predict_carbon",
    "detect_anomaly",
    "calculate_risk_score",
    "generate_recommendations",
    "estimate_savings",
    "estimate_roi",
    "simulate",
    "compare_scenarios",
]
