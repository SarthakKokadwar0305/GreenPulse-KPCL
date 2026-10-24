"""
GreenPulse AI - Dashboard Pydantic Schemas
Defines executive telemetry, KPIs, and quick-action response contracts.
"""
from typing import List, Optional
from pydantic import BaseModel
from app.schemas.common import StatusBadge, TrendIndicator


class KpiMetricSchema(BaseModel):
    id: str
    title: str
    value: float
    decimals: int = 0
    prefix: Optional[str] = None
    unit: Optional[str] = None
    icon_key: str
    trend: TrendIndicator
    status: StatusBadge
    description: str
    sparkline: List[float]


class PlantStatusMetricSchema(BaseModel):
    id: str
    title: str
    value: str
    caption: str
    icon_key: str
    tone: str
    progress: Optional[float] = None


class SystemStatusSchema(BaseModel):
    version: str
    backend: str = "operational"
    ai_engine: str = "operational"
    scada_gateway: str = "connected"
    last_synced_at: str
    latency_ms: float


class DashboardOverviewResponse(BaseModel):
    plant_name: str
    plant_kpis: List[KpiMetricSchema]
    todays_energy_kwh: float
    todays_cost_inr: float
    current_demand_kw: float
    active_machines_count: int
    total_machines_count: int
    daily_carbon_tons: float
    active_alerts_count: int
    predicted_monthly_savings_inr: float
    system_status: SystemStatusSchema
