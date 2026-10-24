"""
GreenPulse AI - Production AI Response Schemas
Defines standardized enterprise contracts incorporating:
- Predictions & Confidence
- SHAP Feature Attributions & Natural Language Explanations
- Dynamic Threshold Evaluations
- Triggered Industrial Business Rules
- Quantified Business, Financial & ESG Impacts
- Model Versioning & Audit Timestamps
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AiFeatureContributionSchema(BaseModel):
    feature: str = Field(description="Raw internal feature column name")
    readable_name: str = Field(description="Human-readable industrial sensor label")
    shap_value: float = Field(description="SHAP game-theoretic contribution value")
    impact_direction: str = Field(description="'up' if increasing prediction, 'down' if decreasing")
    absolute_impact: float = Field(description="Absolute magnitude of contribution")
    feature_value: Optional[float] = Field(default=None, description="Preprocessed feature value")


class AiExplanationPayload(BaseModel):
    base_value: float = Field(description="Expected model baseline prior to local feature additions")
    top_contributing_features: List[AiFeatureContributionSchema]
    positive_contributions: List[AiFeatureContributionSchema] = Field(description="Features driving demand up")
    negative_contributions: List[AiFeatureContributionSchema] = Field(description="Features driving demand down")
    natural_language_explanation: str = Field(description="Domain-grounded explanation for plant engineers")
    xai_method: str = Field(default="SHAP (TreeExplainer Game-Theoretic Attribution)")


class AiThresholdStatusSchema(BaseModel):
    machine_id: str
    machine_name: str
    department: str
    metric: str
    unit: str
    current_value: float
    expected_value: float
    lower_threshold: float
    upper_threshold: float
    critical_upper_threshold: Optional[float] = None
    deviation: float
    deviation_pct: float
    severity: str  # Normal, Information, Warning, Critical, Emergency
    confidence: float
    reason: str


class AiTriggeredRuleSchema(BaseModel):
    rule_id: str
    rule_name: str
    module: str
    category: str
    priority: str
    condition_observed: str
    reason: str
    suggested_action: str
    operational_impact: str
    confidence: float
    expected_savings: Dict[str, float]


class AiBusinessImpactSummary(BaseModel):
    monthly_total_savings_inr: float
    annual_total_savings_inr: float
    monthly_kwh_saved: float
    monthly_carbon_reduction_kg: float
    annual_carbon_tonnes_co2e: float
    avoided_downtime_hours_per_month: float
    roi: str
    payback_period: str
