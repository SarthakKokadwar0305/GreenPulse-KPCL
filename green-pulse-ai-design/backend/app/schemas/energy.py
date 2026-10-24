"""
GreenPulse AI - Energy Explorer Pydantic Schemas
Contracts for hourly, daily, weekly, and monthly profiles, comparisons, peak demand, and 7x24 heatmap.
"""
from typing import List, Optional
from pydantic import BaseModel


class HourlyUsagePoint(BaseModel):
    hour: str
    actual_kw: float
    baseline_kw: float
    tariff_rate: float
    is_peak_tariff: bool


class DailyUsagePoint(BaseModel):
    date: str
    day: str
    energy_kwh: float
    cost: float
    target_kwh: float


class WeeklyUsagePoint(BaseModel):
    week: str
    energy_kwh: float
    baseline_kwh: float
    weekend_ratio_percent: float


class MonthlyUsagePoint(BaseModel):
    month: str
    energy_mwh: float
    budget_mwh: float
    cost_lakhs: float


class MachineComparisonPoint(BaseModel):
    machine: str
    current_kw: float
    energy_kwh: float
    share_percent: float
    color: str


class DepartmentComparisonPoint(BaseModel):
    department: str
    power_kw: float
    share_percent: float
    cost_per_hour: float


class PeakDemandAnalyticsSchema(BaseModel):
    peak_time: str
    peak_recorded_kw: float
    penalty_threshold_kw: float
    power_factor_at_peak: float
    exceedance_risk_percent: float


class HeatmapDayRow(BaseModel):
    day: str
    hours: List[int]


class EnergyAnalyticsResponse(BaseModel):
    current_demand_kw: float
    contracted_peak_limit_kw: float
    peak_headroom_kw: float
    today_total_kwh: float
    estimated_daily_cost: float
    hourly_trend: List[HourlyUsagePoint]
    daily_trend: List[DailyUsagePoint]
    weekly_trend: List[WeeklyUsagePoint]
    monthly_trend: List[MonthlyUsagePoint]
    machine_comparison: List[MachineComparisonPoint]
    department_comparison: List[DepartmentComparisonPoint]
    peak_demand: PeakDemandAnalyticsSchema
    heatmap_7x24: List[HeatmapDayRow]
