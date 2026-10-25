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


class MachineSimulationRequest(BaseModel):
    machine_id: str
    machine_state: str = Field(default="running", description="running | idle | maintenance | fault | emergency_stop")
    runtime_hours: float = Field(default=16.0, ge=0.0, le=24.0)
    production_load_percent: float = Field(default=85.0, ge=0.0, le=100.0)
    motor_speed_percent: float = Field(default=85.0, ge=0.0, le=100.0)
    temperature_c: float = Field(default=65.0)
    voltage_v: float = Field(default=400.0, ge=180.0, le=500.0)
    current_a: float = Field(default=30.0, ge=0.0, le=2500.0)
    power_factor: float = Field(default=0.92, ge=0.50, le=1.0)
    renewable_share_percent: float = Field(default=22.0, ge=0.0, le=100.0)
    maintenance_condition: str = Field(default="good", description="excellent | good | warning | critical")


class MachineSimulationResponse(BaseModel):
    machine_id: str
    machine_name: str
    machine_code: str
    machine_state: str
    runtime_hours: float
    production_load_percent: float
    motor_speed_percent: float
    temperature_c: float
    voltage_v: float
    current_a: float
    power_factor: float
    renewable_share_percent: float
    maintenance_condition: str

    # AI Predictions
    predicted_power_kw: float
    predicted_energy_kwh: float
    predicted_cost_inr: float
    predicted_carbon_kg: float
    machine_health_percent: float
    equipment_efficiency_percent: float
    failure_probability_percent: float
    peak_demand_contribution_kw: float
    expected_downtime_hours: float
    remaining_useful_life_days: float
    operational_risk: str  # Low | Moderate | High | Severe
    oee_percent: float
    confidence_score: float

    # Explanations & Prescriptive Insights
    explanations: List[str]
    prescriptive_insights: List[str]

    # Deltas compared to baseline
    baseline_energy_kwh: float
    delta_energy_percent: float
    baseline_cost_inr: float
    delta_cost_percent: float
    baseline_carbon_kg: float
    delta_carbon_percent: float
    baseline_health_score: float
    delta_health_percent: float

    # 24-hour profile
    hourly_power_profile: List[HourlySimulationPoint]
    timestamp: str
    model_version: str = "2.4.0-twin"


class SimulationTimelineEntry(BaseModel):
    id: Optional[str] = None
    timestamp: str
    machine_id: str
    machine_name: str
    changed_parameters: List[str]
    previous_values: dict
    predicted_values: dict
    user: str = "Industrial Operator"


class MachineScenario(BaseModel):
    scenario_name: str
    request: MachineSimulationRequest
    response: Optional[MachineSimulationResponse] = None

