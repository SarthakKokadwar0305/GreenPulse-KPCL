"""
GreenPulse AI - ML Simulator Interface
Executes parametric thermodynamic and electricity tariff counterfactual simulations.
"""
from typing import Any, Dict, List


def simulate(
    production_load_pct: float = 100.0,
    runtime_hours: float = 16.0,
    shift_schedule: str = "2-shift",
    base_tariff: float = 7.20,
    renewable_pct: float = 22.0,
    baseline_energy_kwh: float = 31450.0,
    baseline_cost: float = 226440.0,
    baseline_carbon_tons: float = 25.79
) -> Dict[str, Any]:
    """
    Simulates plant energy, financial cost, and carbon abatement under adjusted operational parameters.
    """
    load_factor = production_load_pct / 100.0
    runtime_factor = runtime_hours / 16.0
    
    shift_multiplier = 1.0
    if shift_schedule == "1-shift":
        shift_multiplier = 0.55
    elif shift_schedule == "3-shift":
        shift_multiplier = 1.38
    elif shift_schedule == "night-shift":
        shift_multiplier = 0.88

    # Simulated Energy Consumption
    simulated_kwh = round(baseline_energy_kwh * load_factor * runtime_factor * shift_multiplier * 0.95, 1)

    # Effective Tariff calculation
    effective_tariff = base_tariff
    if shift_schedule == "night-shift":
        effective_tariff = base_tariff * 0.78
    elif shift_schedule == "3-shift":
        effective_tariff = base_tariff * 1.05

    # Grid vs Solar calculation
    solar_share = min(1.0, max(0.0, renewable_pct / 100.0))
    grid_share = max(0.0, 1.0 - solar_share)
    grid_kwh = simulated_kwh * grid_share

    simulated_cost = round(grid_kwh * effective_tariff, 2)
    simulated_carbon = round((grid_kwh * 0.82) / 1000.0, 2)

    delta_energy_kwh = round(simulated_kwh - baseline_energy_kwh, 1)
    delta_energy_pct = round((delta_energy_kwh / baseline_energy_kwh) * 100.0, 1)

    delta_cost = round(simulated_cost - baseline_cost, 2)
    delta_cost_pct = round((delta_cost / baseline_cost) * 100.0, 1)

    delta_carbon = round(simulated_carbon - baseline_carbon_tons, 2)
    delta_carbon_pct = round((delta_carbon / baseline_carbon_tons) * 100.0, 1)

    monthly_savings = round(-delta_cost * 30.0, 2)

    return {
        "inputs": {
            "production_load_percent": production_load_pct,
            "machine_runtime_hours": runtime_hours,
            "shift_schedule": shift_schedule,
            "base_tariff_per_kwh": base_tariff,
            "renewable_share_percent": renewable_pct,
        },
        "baseline": {
            "daily_energy_kwh": baseline_energy_kwh,
            "daily_cost": baseline_cost,
            "daily_carbon_tons": baseline_carbon_tons,
        },
        "simulated": {
            "daily_energy_kwh": simulated_kwh,
            "daily_cost": simulated_cost,
            "daily_carbon_tons": simulated_carbon,
        },
        "deltas": {
            "energy_kwh": delta_energy_kwh,
            "energy_percent": delta_energy_pct,
            "cost": delta_cost,
            "cost_percent": delta_cost_pct,
            "carbon_tons": delta_carbon,
            "carbon_percent": delta_carbon_pct,
        },
        "monthly_net_savings_currency": monthly_savings,
    }


def compare_scenarios(
    scenarios: List[Dict[str, Any]],
    baseline_energy_kwh: float = 31450.0
) -> List[Dict[str, Any]]:
    """
    Evaluates multiple what-if scenario permutations side-by-side.
    """
    results = []
    for sc in scenarios:
        sim = simulate(
            production_load_pct=sc.get("production_load_percent", 100.0),
            runtime_hours=sc.get("machine_runtime_hours", 16.0),
            shift_schedule=sc.get("shift_schedule", "2-shift"),
            base_tariff=sc.get("base_tariff_per_kwh", 7.20),
            renewable_pct=sc.get("renewable_share_percent", 22.0),
            baseline_energy_kwh=baseline_energy_kwh
        )
        sim["scenario_name"] = sc.get("name", "Unnamed Scenario")
        results.append(sim)
    return results
