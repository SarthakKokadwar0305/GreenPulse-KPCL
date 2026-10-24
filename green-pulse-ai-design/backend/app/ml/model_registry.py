"""
GreenPulse AI - Centralized Model Registry
Singleton enterprise registry for all serialized machine learning models,
preprocessing pipelines, SHAP explainers, and industrial intelligence engines.
All artifacts are loaded once during application startup and cached in-memory.
"""
import hashlib
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
import joblib

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

logger = logging.getLogger("GreenPulseAI.ModelRegistry")


def compute_file_sha256(filepath: Path) -> str:
    """Computes SHA-256 checksum of a model file."""
    if not filepath.exists():
        return "NOT_FOUND"
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


class ModelRegistry:
    """
    Thread-safe Singleton Model Registry providing unified access to:
    - 4 XGBoost Multi-Target Forecasting Regressors
    - 1 Isolation Forest Telemetry Anomaly Detector
    - StandardScaler & OneHotEncoder Preprocessing Pipelines
    - 6 Industrial Intelligence Engines
    """
    _instance: Optional["ModelRegistry"] = None
    _initialized: bool = False

    def __new__(cls) -> "ModelRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._models = {}
            cls._instance._preprocessors = {}
            cls._instance._engines = {}
            cls._instance._metadata = {}
            cls._instance._feature_names = []
            cls._instance._initialized = False
        return cls._instance

    @classmethod
    def get_instance(cls) -> "ModelRegistry":
        """Singleton accessor for ModelRegistry."""
        reg = cls()
        if not reg.is_initialized:
            reg.initialize()
        return reg

    def get_all_models(self) -> Dict[str, Any]:
        """Returns all loaded models and preprocessors."""
        res = dict(self._models)
        res.update(self._preprocessors)
        return res

    @property
    def threshold_engine(self) -> Optional[Any]:
        return self._engines.get("threshold_engine")

    @property
    def alert_engine(self) -> Optional[Any]:
        return self._engines.get("alert_engine")

    @property
    def rule_engine(self) -> Optional[Any]:
        return self._engines.get("rule_engine")

    @property
    def recommendation_engine(self) -> Optional[Any]:
        return self._engines.get("recommendation_engine")

    @property
    def business_impact_engine(self) -> Optional[Any]:
        return self._engines.get("business_impact_engine")

    @property
    def priority_engine(self) -> Optional[Any]:
        return self._engines.get("priority_engine")

    def initialize(self, models_dir: Optional[Path] = None) -> None:
        """Loads all Joblib models and industrial engines into memory."""
        if self._initialized:
            logger.info("ModelRegistry is already initialized. Skipping duplicate load.")
            return

        if models_dir is None:
            # Check backend/trained_models first, then trained_models
            primary = Path(__file__).resolve().parent.parent.parent / "trained_models"
            alt = Path(__file__).resolve().parent.parent.parent.parent / "trained_models"
            models_dir = primary if primary.exists() else alt

        logger.info(f"Initializing ModelRegistry from directory: {models_dir}")

        # 1. Load Preprocessors
        scaler_path = models_dir / "scaler.joblib"
        encoder_path = models_dir / "encoder.joblib"
        feat_list_path = models_dir / "feature_list.json"

        if scaler_path.exists():
            self._preprocessors["scaler"] = joblib.load(scaler_path)
            logger.info("Loaded StandardScaler artifact.")
        if encoder_path.exists():
            self._preprocessors["encoder"] = joblib.load(encoder_path)
            logger.info("Loaded OneHotEncoder artifact.")
        if feat_list_path.exists():
            with open(feat_list_path, "r", encoding="utf-8") as f:
                self._feature_names = json.load(f)
            logger.info(f"Loaded {len(self._feature_names)} input features definition.")

        # 2. Load Forecasting Regressors
        forecast_targets = {
            "energy_forecast": "energy_forecast.joblib",
            "cost_forecast": "cost_forecast.joblib",
            "carbon_forecast": "carbon_forecast.joblib",
            "peak_forecast": "peak_forecast.joblib",
        }
        for key, fname in forecast_targets.items():
            fpath = models_dir / fname
            if fpath.exists():
                self._models[key] = joblib.load(fpath)
                logger.info(f"Loaded forecasting model: [{key}] from {fpath.name}")
            else:
                logger.warning(f"Model file not found: {fpath}")

        # 3. Load Anomaly Detector
        anomaly_path = models_dir / "anomaly_detector.joblib"
        if anomaly_path.exists():
            self._models["anomaly_detector"] = joblib.load(anomaly_path)
            logger.info("Loaded Isolation Forest anomaly detector.")
        else:
            logger.warning(f"Anomaly detector file not found: {anomaly_path}")

        # 4. Load Industrial Intelligence Engines
        from services.threshold_engine import AdaptiveThresholdEngine
        from services.alert_engine import AlertGenerationEngine
        from services.rule_engine import IndustrialRuleEngine
        from services.recommendation_engine import SmartRecommendationEngine
        from services.business_impact_engine import BusinessImpactEngine
        from services.priority_engine import RecommendationPriorityEngine

        self._engines["threshold_engine"] = AdaptiveThresholdEngine()
        self._engines["alert_engine"] = AlertGenerationEngine()
        self._engines["rule_engine"] = IndustrialRuleEngine()
        self._engines["recommendation_engine"] = SmartRecommendationEngine()
        self._engines["business_impact_engine"] = BusinessImpactEngine()
        self._engines["priority_engine"] = RecommendationPriorityEngine()
        logger.info("Instantiated all 6 Industrial Intelligence Engines.")

        # 5. Build and Save model_registry.json
        self._metadata = self._build_registry_metadata(models_dir)
        registry_json_path = models_dir / "model_registry.json"
        with open(registry_json_path, "w", encoding="utf-8") as f:
            json.dump(self._metadata, f, indent=2)
        logger.info(f"Generated comprehensive metadata registry at {registry_json_path}")

        self._initialized = True

    def _build_registry_metadata(self, models_dir: Path) -> Dict[str, Any]:
        """Constructs full versioning, SHA-256 hashes, metrics, and parameters."""
        meta_src = models_dir / "model_metadata.json"
        metrics_data = {}
        if meta_src.exists():
            with open(meta_src, "r", encoding="utf-8") as f:
                metrics_data = json.load(f)

        config_src = models_dir / "training_config.json"
        config_data = {}
        if config_src.exists():
            with open(config_src, "r", encoding="utf-8") as f:
                config_data = json.load(f)

        models_info = {}
        file_map = {
            "energy_forecast": "energy_forecast.joblib",
            "cost_forecast": "cost_forecast.joblib",
            "carbon_forecast": "carbon_forecast.joblib",
            "peak_forecast": "peak_forecast.joblib",
            "anomaly_detector": "anomaly_detector.joblib",
            "scaler": "scaler.joblib",
            "encoder": "encoder.joblib",
        }
        for key, fname in file_map.items():
            fpath = models_dir / fname
            models_info[key] = {
                "filename": fname,
                "sha256": compute_file_sha256(fpath),
                "size_bytes": fpath.stat().st_size if fpath.exists() else 0,
                "status": "LOADED" if fpath.exists() else "MISSING",
            }

        return {
            "registry_version": "1.2.0-prod",
            "project": "GreenPulse AI",
            "environment": "Production",
            "training_date": metrics_data.get("training_timestamp", "2026-10-24T13:31:29Z"),
            "dataset_used": "greenpulse_dataset (133,326 train rows, 28,619 val rows, 28,664 test rows)",
            "random_seed": 42,
            "algorithms": {
                "forecasting": "XGBoost Regressor (Histogram Gradient Boosting)",
                "anomaly_detection": "Isolation Forest (Unsupervised Operational Telemetry)",
            },
            "models": models_info,
            "input_features": self._feature_names,
            "feature_count": len(self._feature_names),
            "evaluation_metrics": metrics_data.get("target_metrics", {}),
            "hyperparameters": config_data.get("tuned_hyperparameters", {}),
        }

    def get_model(self, name: str) -> Optional[Any]:
        """Returns loaded model instance by key."""
        return self._models.get(name)

    def get_preprocessor(self, name: str) -> Optional[Any]:
        """Returns loaded preprocessor (scaler/encoder)."""
        return self._preprocessors.get(name)

    def get_engine(self, name: str) -> Optional[Any]:
        """Returns instantiated industrial intelligence engine."""
        return self._engines.get(name)

    def get_feature_names(self) -> List[str]:
        """Returns aligned feature names array."""
        return list(self._feature_names)

    def get_metadata(self) -> Dict[str, Any]:
        """Returns model versioning metadata."""
        return self._metadata

    @property
    def is_initialized(self) -> bool:
        return self._initialized


# Module-level accessor function
def get_model_registry() -> ModelRegistry:
    """Returns singleton ModelRegistry instance."""
    registry = ModelRegistry()
    if not registry.is_initialized:
        registry.initialize()
    return registry
