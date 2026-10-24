"""
GreenPulse AI - Anomaly Pydantic Schemas
Contracts for incident cards, telemetry evidence, and status updates.
"""
from typing import List, Optional
from pydantic import BaseModel


class AnomalyEvidenceItem(BaseModel):
    metric: str
    measured: str
    expected: str
    z_score: float


class AnomalyIncidentSchema(BaseModel):
    id: str
    machine_id: str
    machine_name: str
    zone: str
    severity: str  # 'critical', 'warning', 'info'
    status: str  # 'open', 'investigating', 'acknowledged', 'resolved'
    detected_at: str
    duration_minutes: int
    root_cause: str
    evidence: List[AnomalyEvidenceItem]
    confidence_percent: float
    suggested_action: str
    estimated_cost_impact_per_hour: float
    currency: str
    assigned_engineer: Optional[str] = None
    work_order_id: Optional[str] = None
    
    # Production AI Integration Fields
    anomaly_score: Optional[float] = None
    threshold_violated: Optional[str] = None
    triggered_rules: Optional[List[str]] = None
    recommended_action: Optional[str] = None
    model_version: Optional[str] = "1.2.0-prod"


class AcknowledgeAnomalyRequest(BaseModel):
    engineer_name: str
    notes: Optional[str] = None


class CreateWorkOrderRequest(BaseModel):
    priority: str = "High"
    assigned_technician: str
    instructions: Optional[str] = None
