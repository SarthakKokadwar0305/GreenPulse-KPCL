"""
GreenPulse AI - Machine Pydantic Schemas
Contracts for Digital Twin machinery, 3-phase diagnostics, and telemetry drawer.
"""
from typing import List, Optional
from pydantic import BaseModel


class VoltageBalance(BaseModel):
    l1: float
    l2: float
    l3: float
    line_to_line: float
    unbalance_percent: float


class PhaseCurrent(BaseModel):
    l1: float
    l2: float
    l3: float


class MaintenanceRecordSchema(BaseModel):
    date: str
    type: str
    technician: str
    notes: str


class MachineInsightSchema(BaseModel):
    title: str
    explanation: str
    severity: str
    suggested_remedy: str
    potential_savings_kw: float


class MachineTimelineState(BaseModel):
    time: str
    state: str
    power: float


class MachineDetailSchema(BaseModel):
    id: str
    name: str
    code: str
    category: str
    zone: str
    status: str  # 'running' (green), 'warning' (yellow), 'fault' (red), 'idle' (blue)
    power_kw: float
    rated_power_kw: float
    temperature_c: float
    thermal_threshold_c: float
    voltage: VoltageBalance
    current: PhaseCurrent
    power_factor: float
    runtime_hours_total: float
    runtime_hours_shift: float
    mtbf_hours: float
    mttr_hours: float
    health_score: int
    degradation_rate_percent: float
    failure_probability_72h: float  # AI model placeholder
    likely_failure_mode: str
    carbon_kg_per_hour: float
    carbon_today_kg: float
    carbon_share_percent: float
    energy_today_kwh: float
    last_maintenance_date: str
    next_scheduled_pm: str
    maintenance_history: List[MaintenanceRecordSchema]
    ai_insight: MachineInsightSchema
    timeline_24h: List[MachineTimelineState]
    specs: dict
