"""
Tests for SHAP TreeExplainer and Natural Language Generation.
"""
import numpy as np
import pytest
from app.ml.shap_explainer import get_shap_engine


def test_shap_engine_initialization():
    """Verify SHAP explainer initializes properly."""
    engine = get_shap_engine()
    assert engine._initialized is True
    assert len(engine._feature_names) == 34


def test_shap_local_explanation():
    """Verify explain_prediction computes positive/negative contributions and narrative."""
    engine = get_shap_engine()
    sample_vector = np.zeros(34)
    # Set active power and rated power
    sample_vector[0] = 0.5   # rated_power_kw
    sample_vector[2] = 1.2   # power_kw
    sample_vector[17] = 0.8  # load_ratio

    explanation = engine.explain_prediction(
        feature_vector=sample_vector,
        top_k=4,
        context={"machine_name": "Air Compressor #1", "hour": 18, "shift": "B"}
    )

    assert "top_contributing_features" in explanation
    assert len(explanation["top_contributing_features"]) <= 4
    assert "positive_contributions" in explanation
    assert "negative_contributions" in explanation
    assert "natural_language_explanation" in explanation
    assert isinstance(explanation["natural_language_explanation"], str)
    assert len(explanation["natural_language_explanation"]) > 20
    assert "SHAP" in explanation["xai_method"]


def test_feature_name_formatting():
    """Verify raw column names convert to readable industrial labels."""
    engine = get_shap_engine()
    label_power = engine._format_feature_name("power_kw")
    label_load = engine._format_feature_name("load_ratio")
    label_temp = engine._format_feature_name("ambient_temp_c")

    assert "Active Power" in label_power
    assert "Utilization" in label_load or "Load" in label_load
    assert "Temperature" in label_temp
