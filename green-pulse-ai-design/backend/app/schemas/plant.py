"""
GreenPulse AI - Plant Overview Pydantic Schemas
Contracts for executive production summaries, departments, shifts, utilities, and timeline.
"""
from typing import List, Optional
from pydantic import BaseModel


class HourlyThroughputPoint(BaseModel):
    hour: str
    target: int
    actual: int


class ProductionSummarySchema(BaseModel):
    target_units: int
    actual_units: int
    throughput_rate_per_hour: int
    first_pass_yield: float
    downtime_minutes: int
    active_lines: int
    total_lines: int
    hourly_throughput: List[HourlyThroughputPoint]


class DepartmentOverviewSchema(BaseModel):
    id: str
    name: str
    zone: str
    power_kw: float
    energy_today_kwh: float
    efficiency: float
    health_score: int
    status: str
    machine_count: int


class UtilityConsumptionSchema(BaseModel):
    id: str
    name: str
    current_rate: float
    unit: str
    capacity: float
    utilization_percent: float
    today_total: float
    status: str


class ActiveUtilityAssetSchema(BaseModel):
    id: str
    name: str
    type: str
    power_kw: float
    load_factor: float
    status: str
    runtime_today_hours: float


class ShiftInformationSchema(BaseModel):
    current_shift: str
    shift_code: str
    time_range: str
    lead_engineer: str
    lead_role: str
    operators_on_floor: int
    maintenance_techs: int
    shift_energy_budget_kwh: float
    shift_energy_consumed_kwh: float
    production_target: int
    production_actual: int
    elapsed_percent: int


class FactoryTimelineEventSchema(BaseModel):
    id: str
    time: str
    title: str
    category: str
    description: str
    severity: str


class PlantOverviewResponse(BaseModel):
    plant_id: str
    plant_name: str
    last_updated: str
    production_summary: ProductionSummarySchema
    departments: List[DepartmentOverviewSchema]
    utilities: List[UtilityConsumptionSchema]
    active_utilities: List[ActiveUtilityAssetSchema]
    shift_info: ShiftInformationSchema
    timeline: List[FactoryTimelineEventSchema]
    health_summary: dict
