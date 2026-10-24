"""
GreenPulse AI - Carbon Accounting Pydantic Schemas
Contracts for Scope 1, Scope 2, department/machine breakdowns, and ESG indices.
"""
from typing import List, Optional
from pydantic import BaseModel


class Scope1SourceItem(BaseModel):
    source: str
    tons: float
    share: float
    activity_data: str


class Scope1Breakdown(BaseModel):
    total_tons: float
    target_tons: float
    breakdown: List[Scope1SourceItem]


class Scope2SourceItem(BaseModel):
    source: str
    tons: float
    share: float


class Scope2Breakdown(BaseModel):
    total_tons: float
    grid_emission_factor_kg_per_kwh: float
    purchased_mwh: float
    renewable_offset_tons: float
    breakdown: List[Scope2SourceItem]


class CarbonTrendPoint(BaseModel):
    month: str
    scope1: float
    scope2: float
    net_total: float
    target: float


class CarbonByMachinePoint(BaseModel):
    machine: str
    carbon_tons: float
    intensity_kg_per_unit: float
    percent: float


class CarbonByDepartmentPoint(BaseModel):
    department: str
    tons: float
    share_percent: float


class EsgOverviewSchema(BaseModel):
    environmental_index: float
    renewable_energy_share_percent: float
    water_recycle_ratio_percent: float
    waste_diverted_percent: float
    gri_compliance: str
    brsr_status: str


class CarbonAccountingResponse(BaseModel):
    today_total_tons: float
    today_target_tons: float
    month_to_date_tons: float
    sustainability_score: int
    sustainability_tier: str
    scope1: Scope1Breakdown
    scope2: Scope2Breakdown
    monthly_trend: List[CarbonTrendPoint]
    by_machine: List[CarbonByMachinePoint]
    by_department: List[CarbonByDepartmentPoint]
    esg_overview: EsgOverviewSchema
