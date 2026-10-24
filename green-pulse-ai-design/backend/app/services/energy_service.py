"""
GreenPulse AI - Energy Service
Multi-resolution energy analytics, peak demand headroom, and 7-day 24h heatmaps.
"""
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.repositories.energy_repository import EnergyRepository
from app.schemas.energy import (
    DailyUsagePoint,
    DepartmentComparisonPoint,
    EnergyAnalyticsResponse,
    HeatmapDayRow,
    HourlyUsagePoint,
    MachineComparisonPoint,
    MonthlyUsagePoint,
    PeakDemandAnalyticsSchema,
    WeeklyUsagePoint,
)


class EnergyService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.energy_repo = EnergyRepository(session)

    async def get_energy_analytics(self, time_range: str = "24h") -> EnergyAnalyticsResponse:
        current_demand = await self.energy_repo.get_total_active_power()
        today_total_kwh = await self.energy_repo.get_total_energy_today()
        contract_limit = settings.CONTRACTED_PEAK_DEMAND_KW
        headroom = round(contract_limit - current_demand, 1)
        est_cost = round(today_total_kwh * settings.BASE_TARIFF_INR, 2)

        hourly_trend = [
            HourlyUsagePoint(hour="00:00", actual_kw=1140.0, baseline_kw=1100.0, tariff_rate=5.20, is_peak_tariff=False),
            HourlyUsagePoint(hour="02:00", actual_kw=1160.0, baseline_kw=1120.0, tariff_rate=5.20, is_peak_tariff=False),
            HourlyUsagePoint(hour="04:00", actual_kw=1240.0, baseline_kw=1200.0, tariff_rate=5.20, is_peak_tariff=False),
            HourlyUsagePoint(hour="06:00", actual_kw=1450.0, baseline_kw=1420.0, tariff_rate=7.20, is_peak_tariff=False),
            HourlyUsagePoint(hour="08:00", actual_kw=1640.0, baseline_kw=1580.0, tariff_rate=7.20, is_peak_tariff=False),
            HourlyUsagePoint(hour="10:00", actual_kw=1710.0, baseline_kw=1680.0, tariff_rate=9.80, is_peak_tariff=True),
            HourlyUsagePoint(hour="12:00", actual_kw=1580.0, baseline_kw=1550.0, tariff_rate=9.80, is_peak_tariff=True),
            HourlyUsagePoint(hour="14:00", actual_kw=1740.0, baseline_kw=1690.0, tariff_rate=7.20, is_peak_tariff=False),
            HourlyUsagePoint(hour="16:00", actual_kw=1520.0, baseline_kw=1550.0, tariff_rate=7.20, is_peak_tariff=False),
            HourlyUsagePoint(hour="18:00", actual_kw=1780.0, baseline_kw=1720.0, tariff_rate=10.40, is_peak_tariff=True),
            HourlyUsagePoint(hour="20:00", actual_kw=1790.0, baseline_kw=1740.0, tariff_rate=10.40, is_peak_tariff=True),
            HourlyUsagePoint(hour="22:00", actual_kw=1390.0, baseline_kw=1350.0, tariff_rate=5.20, is_peak_tariff=False),
        ]

        daily_trend = [
            DailyUsagePoint(date="18 Oct", day="Sun", energy_kwh=18400.0, cost=132480.0, target_kwh=19000.0),
            DailyUsagePoint(date="19 Oct", day="Mon", energy_kwh=31200.0, cost=224640.0, target_kwh=32000.0),
            DailyUsagePoint(date="20 Oct", day="Tue", energy_kwh=32800.0, cost=236160.0, target_kwh=32500.0),
            DailyUsagePoint(date="21 Oct", day="Wed", energy_kwh=32100.0, cost=231120.0, target_kwh=32000.0),
            DailyUsagePoint(date="22 Oct", day="Thu", energy_kwh=33400.0, cost=240480.0, target_kwh=32500.0),
            DailyUsagePoint(date="23 Oct", day="Fri", energy_kwh=31900.0, cost=229680.0, target_kwh=32000.0),
            DailyUsagePoint(date="24 Oct", day="Sat", energy_kwh=26800.0, cost=192960.0, target_kwh=28000.0),
        ]

        weekly_trend = [
            WeeklyUsagePoint(week="Wk 39", energy_kwh=218000.0, baseline_kwh=224000.0, weekend_ratio_percent=18.2),
            WeeklyUsagePoint(week="Wk 40", energy_kwh=212500.0, baseline_kwh=224000.0, weekend_ratio_percent=17.5),
            WeeklyUsagePoint(week="Wk 41", energy_kwh=208400.0, baseline_kwh=220000.0, weekend_ratio_percent=17.1),
            WeeklyUsagePoint(week="Wk 42", energy_kwh=206200.0, baseline_kwh=220000.0, weekend_ratio_percent=16.8),
        ]

        monthly_trend = [
            MonthlyUsagePoint(month="May 2026", energy_mwh=924.0, budget_mwh=960.0, cost_lakhs=66.5),
            MonthlyUsagePoint(month="Jun 2026", energy_mwh=908.0, budget_mwh=940.0, cost_lakhs=65.4),
            MonthlyUsagePoint(month="Jul 2026", energy_mwh=895.0, budget_mwh=930.0, cost_lakhs=64.4),
            MonthlyUsagePoint(month="Aug 2026", energy_mwh=880.0, budget_mwh=920.0, cost_lakhs=63.3),
            MonthlyUsagePoint(month="Sep 2026", energy_mwh=862.0, budget_mwh=910.0, cost_lakhs=62.1),
            MonthlyUsagePoint(month="Oct 2026 (MTD)", energy_mwh=678.0, budget_mwh=900.0, cost_lakhs=48.8),
        ]

        machine_comparison = [
            MachineComparisonPoint(machine="Heat Furnace", current_kw=680.0, energy_kwh=5310.0, share_percent=40.8, color="#1565c0"),
            MachineComparisonPoint(machine="Air Compressor", current_kw=412.0, energy_kwh=3420.0, share_percent=26.3, color="#90a4ae"),
            MachineComparisonPoint(machine="Assembly Line", current_kw=236.0, energy_kwh=2150.0, share_percent=16.5, color="#4f9ae6"),
            MachineComparisonPoint(machine="CNC Machine", current_kw=118.0, energy_kwh=980.0, share_percent=7.5, color="#2e7d32"),
            MachineComparisonPoint(machine="Cooling Pump", current_kw=74.0, energy_kwh=610.0, share_percent=4.7, color="#546e7a"),
            MachineComparisonPoint(machine="Paint Booth", current_kw=36.0, energy_kwh=540.0, share_percent=4.2, color="#f9a825"),
        ]

        department_comparison = [
            DepartmentComparisonPoint(department="Thermal Processing", power_kw=680.0, share_percent=43.7, cost_per_hour=4896.0),
            DepartmentComparisonPoint(department="Utilities Block", power_kw=486.0, share_percent=31.2, cost_per_hour=3499.0),
            DepartmentComparisonPoint(department="Final Assembly", power_kw=236.0, share_percent=15.2, cost_per_hour=1699.0),
            DepartmentComparisonPoint(department="Machining Hall", power_kw=118.0, share_percent=7.6, cost_per_hour=849.0),
            DepartmentComparisonPoint(department="Finishing Line", power_kw=36.0, share_percent=2.3, cost_per_hour=259.0),
        ]

        peak_demand = PeakDemandAnalyticsSchema(
            peak_time="14:15 Today",
            peak_recorded_kw=1740.0,
            penalty_threshold_kw=2375.0,
            power_factor_at_peak=0.94,
            exceedance_risk_percent=4.2,
        )

        heatmap_7x24 = [
            HeatmapDayRow(day="Mon", hours=[35, 34, 33, 38, 48, 62, 75, 82, 88, 92, 94, 95, 84, 89, 93, 86, 82, 85, 96, 98, 94, 88, 55, 42]),
            HeatmapDayRow(day="Tue", hours=[36, 35, 34, 39, 50, 65, 78, 85, 90, 95, 96, 97, 86, 91, 95, 88, 85, 88, 97, 99, 96, 90, 58, 44]),
            HeatmapDayRow(day="Wed", hours=[35, 34, 33, 38, 49, 64, 76, 84, 89, 93, 95, 96, 85, 90, 94, 87, 84, 86, 95, 97, 95, 89, 56, 43]),
            HeatmapDayRow(day="Thu", hours=[37, 36, 35, 40, 52, 66, 79, 86, 91, 96, 98, 99, 88, 92, 96, 89, 86, 89, 98, 100, 97, 91, 60, 45]),
            HeatmapDayRow(day="Fri", hours=[36, 35, 34, 39, 50, 63, 75, 83, 88, 92, 94, 95, 85, 89, 93, 86, 83, 85, 94, 96, 93, 87, 54, 40]),
            HeatmapDayRow(day="Sat", hours=[30, 28, 28, 30, 36, 45, 55, 62, 68, 72, 74, 75, 66, 70, 74, 68, 65, 68, 76, 78, 75, 69, 44, 32]),
            HeatmapDayRow(day="Sun", hours=[24, 22, 22, 24, 28, 32, 38, 44, 48, 52, 54, 55, 48, 50, 53, 49, 46, 48, 55, 58, 54, 48, 32, 26]),
        ]

        return EnergyAnalyticsResponse(
            current_demand_kw=current_demand,
            contracted_peak_limit_kw=contract_limit,
            peak_headroom_kw=headroom,
            today_total_kwh=today_total_kwh,
            estimated_daily_cost=est_cost,
            hourly_trend=hourly_trend,
            daily_trend=daily_trend,
            weekly_trend=weekly_trend,
            monthly_trend=monthly_trend,
            machine_comparison=machine_comparison,
            department_comparison=department_comparison,
            peak_demand=peak_demand,
            heatmap_7x24=heatmap_7x24,
        )
