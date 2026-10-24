"""
GreenPulse AI - Industrial Intelligence Layer: Business Impact Engine
Translates engineering actions and energy savings into quantifiable plant financial and ESG metrics:
Monthly/Annual Cost Savings, Energy Savings, Carbon Abatement, Avoided Downtime, Productivity & Payback.
"""
from typing import Dict, Any, Optional

from services.config.industrial_constants import (
    BASE_TARIFF_INR_PER_KWH,
    PEAK_TARIFF_INR_PER_KWH,
    OFF_PEAK_TARIFF_INR_PER_KWH,
    GRID_EMISSION_FACTOR_KG_PER_KWH,
)


class BusinessImpactEngine:
    """
    Enterprise Industrial Impact Modeling Engine.
    Computes rigorous operational expenditure (OPEX) savings, carbon reductions,
    prevented downtime costs, and payback periods for industrial recommendations.
    """

    def __init__(self):
        # Average blended industrial operating parameters
        self.operating_days_per_month = 26.0
        self.operating_days_per_year = 312.0
        self.operating_hours_per_day = 24.0
        self.avg_blended_tariff = 7.85  # INR / kWh weighted average across ToD shifts
        self.downtime_hourly_cost_inr = 35000.0  # Average factory stoppage cost per hour

    def calculate_impact(
        self,
        hourly_kwh_saved: float,
        daily_operating_hours_affected: float = 8.0,
        hourly_inr_saved: Optional[float] = None,
        avoided_downtime_hours_per_month: float = 0.0,
        productivity_gain_pct: float = 0.0,
        capex_inr: float = 0.0,
        risk_level: str = "Low",
    ) -> Dict[str, Any]:
        """
        Calculates structured financial and ESG impact metrics.
        
        Args:
            hourly_kwh_saved: Active power reduction rate in kWh per hour
            daily_operating_hours_affected: Hours per day the measure is effective
            hourly_inr_saved: Direct hourly financial savings (if null, computed via blended tariff)
            avoided_downtime_hours_per_month: Expected unplanned stoppage prevented
            productivity_gain_pct: Production throughput enhancement (%)
            capex_inr: Capital expenditure required (0 for operational adjustment)
            risk_level: Industrial operational risk reduction classification
            
        Returns:
            Structured JSON impact analysis dictionary.
        """
        # 1. Energy Savings
        daily_kwh = hourly_kwh_saved * daily_operating_hours_affected
        monthly_kwh = daily_kwh * self.operating_days_per_month
        annual_kwh = daily_kwh * self.operating_days_per_year

        # 2. Direct Financial Savings (OPEX)
        if hourly_inr_saved is not None and hourly_inr_saved > 0:
            daily_inr = hourly_inr_saved * daily_operating_hours_affected
        else:
            daily_inr = daily_kwh * self.avg_blended_tariff

        monthly_opex_inr = daily_inr * self.operating_days_per_month
        annual_opex_inr = daily_inr * self.operating_days_per_year

        # 3. Avoided Downtime Value
        monthly_downtime_savings_inr = avoided_downtime_hours_per_month * self.downtime_hourly_cost_inr
        annual_downtime_savings_inr = monthly_downtime_savings_inr * 12.0

        # Total Financial Impact
        monthly_total_savings_inr = monthly_opex_inr + monthly_downtime_savings_inr
        annual_total_savings_inr = annual_opex_inr + annual_downtime_savings_inr

        # 4. Carbon Abatement (Scope 2 Indirect Emissions)
        monthly_carbon_kg = monthly_kwh * GRID_EMISSION_FACTOR_KG_PER_KWH
        annual_carbon_kg = annual_kwh * GRID_EMISSION_FACTOR_KG_PER_KWH
        annual_carbon_tonnes = annual_carbon_kg / 1000.0

        # 5. Financial ROI & Payback Period
        if capex_inr <= 0.0:
            payback_period = "Immediate (Zero CAPEX / Operational Adjustment)"
            payback_months = 0.0
            roi_pct = 999.0
        else:
            payback_months = capex_inr / max(monthly_total_savings_inr, 1.0)
            payback_period = f"{payback_months:.1f} months"
            annual_net_benefit = annual_total_savings_inr - (capex_inr / 3.0)  # 3-year depreciation
            roi_pct = round((annual_net_benefit / capex_inr) * 100.0, 1)

        # 6. ESG & Governance Rating Impact (Points on 100-pt BRSR / ISO 50001 scale)
        esg_points = min(15.0, round((annual_carbon_tonnes * 0.45) + (productivity_gain_pct * 0.8), 2))

        return {
            "energy_savings": {
                "hourly_kwh": round(hourly_kwh_saved, 2),
                "daily_kwh": round(daily_kwh, 2),
                "monthly_kwh": round(monthly_kwh, 2),
                "annual_kwh": round(annual_kwh, 2),
            },
            "financial_savings": {
                "monthly_direct_opex_inr": round(monthly_opex_inr, 2),
                "annual_direct_opex_inr": round(annual_opex_inr, 2),
                "monthly_avoided_downtime_inr": round(monthly_downtime_savings_inr, 2),
                "annual_avoided_downtime_inr": round(annual_downtime_savings_inr, 2),
                "monthly_total_savings_inr": round(monthly_total_savings_inr, 2),
                "annual_total_savings_inr": round(annual_total_savings_inr, 2),
            },
            "carbon_reduction": {
                "monthly_carbon_kg_co2e": round(monthly_carbon_kg, 2),
                "annual_carbon_kg_co2e": round(annual_carbon_kg, 2),
                "annual_carbon_tonnes_co2e": round(annual_carbon_tonnes, 3),
            },
            "operational_reliability": {
                "avoided_downtime_hours_per_month": round(avoided_downtime_hours_per_month, 1),
                "annual_avoided_downtime_hours": round(avoided_downtime_hours_per_month * 12.0, 1),
                "productivity_improvement_pct": round(productivity_gain_pct, 1),
                "risk_reduction": risk_level,
            },
            "investment_economics": {
                "capex_required_inr": round(capex_inr, 2),
                "payback_period": payback_period,
                "payback_months": round(payback_months, 1),
                "roi_percent": roi_pct,
                "esg_score_improvement_pts": esg_points,
            },
        }
