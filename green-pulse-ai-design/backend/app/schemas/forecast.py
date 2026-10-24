"""
GreenPulse AI - Forecast Pydantic Schemas
Contracts for ML multi-horizon predictions, confidence intervals, and explainability.
"""
from typing import List, Optional
from pydantic import BaseModel


class HourlyForecastPoint(BaseModel):
    time: str
    actual_kw: Optional[float] = None
    forecast_kw: float
    lower_bound_80: float
    upper_bound_80: float
    lower_bound_95: float
    upper_bound_95: float
    temperature_c: float
    scheduled_activity: Optional[str] = None


class PrimaryDriverSchema(BaseModel):
    factor: str
    impact_kw: str
    direction: str  # 'up', 'down'
    rationale: str


class AiExplanationSchema(BaseModel):
    primary_drivers: List[PrimaryDriverSchema]
    model_confidence_note: str
    peak_spike_warning: str


class ForecastTimelineMilestoneSchema(BaseModel):
    time: str
    event: str
    impact: str
    recommendation: str
    severity: str


from app.schemas.ai_response import (
    AiExplanationPayload,
    AiFeatureContributionSchema,
    AiThresholdStatusSchema,
    AiTriggeredRuleSchema,
)


class ForecastResponse(BaseModel):
    forecast_range: str
    generated_at: str
    model_architecture: str
    r2_score: float
    projected_day_energy_kwh: float
    projected_cost: float
    projected_carbon_tons: float
    projected_peak_demand_kw: float
    peak_hour: str
    hourly_forecast: List[HourlyForecastPoint]
    ai_explanation: AiExplanationSchema
    timeline_milestones: List[ForecastTimelineMilestoneSchema]
    
    # Production AI Integration Fields
    model_version: Optional[str] = "1.2.0-prod"
    confidence_score: Optional[float] = 0.96
    prediction_timestamp: Optional[str] = None
    shap_explanation: Optional[AiExplanationPayload] = None
    feature_importance: Optional[List[AiFeatureContributionSchema]] = None
    threshold_status: Optional[List[AiThresholdStatusSchema]] = None
    triggered_rules: Optional[List[AiTriggeredRuleSchema]] = None

