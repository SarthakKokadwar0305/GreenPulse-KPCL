"""
GreenPulse AI - Recommendation Pydantic Schemas
Contracts for prescriptive energy saving strategies and action triggers.
"""
from typing import List, Optional
from pydantic import BaseModel


class RecommendationSchema(BaseModel):
    id: str
    title: str
    machine_name: str
    category: str
    priority: str
    estimated_savings_kwh_per_month: float
    estimated_savings_currency_per_month: float
    estimated_carbon_reduction_tons_per_month: float
    payback_period_months: float
    roi_percent: float
    confidence_percent: float
    rationale: str
    action_steps: List[str]
    applied: bool
    applied_at: Optional[str] = None
    
    # Production AI Integration Fields
    business_explanation: Optional[str] = None
    technical_explanation: Optional[str] = None
    supporting_rule_ids: Optional[List[str]] = None
    estimated_downtime_avoided_hrs: Optional[float] = None
    implementation_difficulty: Optional[str] = None
    expected_payback: Optional[str] = None
    model_version: Optional[str] = "1.2.0-prod"


class ApplyRecommendationRequest(BaseModel):
    override_parameters: Optional[dict] = None
    applied_by: str = "Lead Engineer"
