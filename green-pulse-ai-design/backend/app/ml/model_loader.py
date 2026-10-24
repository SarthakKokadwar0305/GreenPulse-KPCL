"""
GreenPulse AI - ML Model Loader
Centralized loader delegating to the production ModelRegistry.
Guarantees models are loaded once during FastAPI lifespan startup and cached in-memory.
"""
from typing import Any, Dict
from app.ml.model_registry import get_model_registry, ModelRegistry


def load_forecasting_model(target: str = "energy_forecast") -> Any:
    """Returns the loaded XGBoost forecasting model singleton."""
    registry = get_model_registry()
    model = registry.get_model(target)
    if model is None:
        model = registry.get_model("energy_forecast")
    return model


def load_anomaly_model() -> Any:
    """Returns the loaded Isolation Forest anomaly detector singleton."""
    registry = get_model_registry()
    return registry.get_model("anomaly_detector")


def load_models() -> Dict[str, Any]:
    """Loads all model artifacts during FastAPI application lifecycle startup."""
    registry = get_model_registry()
    return {
        "energy_forecast": registry.get_model("energy_forecast"),
        "cost_forecast": registry.get_model("cost_forecast"),
        "carbon_forecast": registry.get_model("carbon_forecast"),
        "peak_forecast": registry.get_model("peak_forecast"),
        "anomaly_detector": registry.get_model("anomaly_detector"),
        "scaler": registry.get_preprocessor("scaler"),
        "encoder": registry.get_preprocessor("encoder"),
        "threshold_engine": registry.get_engine("threshold_engine"),
        "alert_engine": registry.get_engine("alert_engine"),
        "rule_engine": registry.get_engine("rule_engine"),
        "recommendation_engine": registry.get_engine("recommendation_engine"),
    }
