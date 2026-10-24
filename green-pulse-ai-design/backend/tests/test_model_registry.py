"""
Tests for Centralized ModelRegistry Singleton and Model Artifact Loading.
"""
import pytest
from app.ml.model_registry import get_model_registry, ModelRegistry


def test_model_registry_singleton():
    """Verify ModelRegistry enforces singleton pattern."""
    reg1 = get_model_registry()
    reg2 = get_model_registry()
    assert reg1 is reg2
    assert reg1.is_initialized is True


def test_model_registry_models_loaded():
    """Verify all 4 forecasting models and anomaly detector are loaded."""
    registry = get_model_registry()
    assert registry.get_model("energy_forecast") is not None
    assert registry.get_model("cost_forecast") is not None
    assert registry.get_model("carbon_forecast") is not None
    assert registry.get_model("peak_forecast") is not None
    assert registry.get_model("anomaly_detector") is not None


def test_model_registry_preprocessors():
    """Verify StandardScaler and OneHotEncoder are loaded with 34 features."""
    registry = get_model_registry()
    assert registry.get_preprocessor("scaler") is not None
    assert registry.get_preprocessor("encoder") is not None
    feature_names = registry.get_feature_names()
    assert len(feature_names) == 34
    assert "power_kw" in feature_names
    assert "rated_power_kw" in feature_names


def test_model_registry_metadata_and_hashes():
    """Verify metadata contains version, training date, SHA-256 hashes and metrics."""
    registry = get_model_registry()
    meta = registry.get_metadata()
    assert meta["registry_version"] == "1.2.0-prod"
    assert "sha256" in meta["models"]["energy_forecast"]
    assert meta["models"]["energy_forecast"]["status"] == "LOADED"
    assert len(meta["models"]["energy_forecast"]["sha256"]) == 64  # Valid SHA-256 hex length


def test_model_registry_engines():
    """Verify all 6 industrial intelligence engines are available in registry."""
    registry = get_model_registry()
    assert registry.get_engine("threshold_engine") is not None
    assert registry.get_engine("alert_engine") is not None
    assert registry.get_engine("rule_engine") is not None
    assert registry.get_engine("recommendation_engine") is not None
    assert registry.get_engine("business_impact_engine") is not None
    assert registry.get_engine("priority_engine") is not None
