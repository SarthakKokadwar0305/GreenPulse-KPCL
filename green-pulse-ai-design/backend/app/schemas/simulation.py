"""
GreenPulse AI - Simulation Pydantic Schemas
Contracts for parametric what-if modeling and counterfactual comparisons.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class SimulationRequest(BaseModel):
    production_load_percent: float = Field(default=100.0, ge=50.0, le=150.0)
    machine_runtime_hours: float = Field(default=16.0, ge=4.0, le=24.0)
    shift_schedule: str = Field(default="2-shift")  # 1-shift, 2-shift, 3-shift, night-shift
    base_tariff_per_kwh: float = Field(default=7.20, ge=3.0, le=20.0)
    renewable_share_percent: float = Field(default=22.0, ge=0.0, le=100.0)


class HourlySimulationPoint(BaseModel):
    hour: str
    baseline_kw: float
    simulated_kw: float


class SimulationResponse(BaseModel):
    production_load_percent: float
    machine_runtime_hours: float
    shift_schedule: str
    base_tariff_per_kwh: float
    renewable_share_percent: float
    
    # Baseline vs Simulated
    baseline_daily_energy_kwh: float
    simulated_daily_energy_kwh: float
    delta_energy_kwh: float
    delta_energy_percent: float

    baseline_daily_cost: float
    simulated_daily_cost: float
    delta_cost: float
    delta_cost_percent: float

    baseline_daily_carbon_tons: float
    simulated_daily_carbon_tons: float
    delta_carbon_tons: float
    delta_carbon_percent: float

    monthly_projected_savings_currency: float
    hourly_comparison: List[HourlySimulationPoint]

    # Production AI Integration Fields
    predicted_energy_kwh: Optional[float] = None
    predicted_cost_inr: Optional[float] = None
    predicted_carbon_tons: Optional[float] = None
    savings_inr: Optional[float] = None
    projected_savings_inr: Optional[float] = None
    recommendation_summary: Optional[str] = None
    model_version: Optional[str] = "1.2.0-prod"
    confidence_score: Optional[float] = 0.95
