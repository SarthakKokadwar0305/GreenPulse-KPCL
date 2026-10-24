"""
GreenPulse AI - Carbon Service
GHG Protocol Scope 1 and Scope 2 corporate carbon accounting & ESG scoring.
"""
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.repositories.energy_repository import EnergyRepository
from app.schemas.carbon import (
    CarbonAccountingResponse,
    CarbonByDepartmentPoint,
    CarbonByMachinePoint,
    CarbonTrendPoint,
    EsgOverviewSchema,
    Scope1Breakdown,
    Scope1SourceItem,
    Scope2Breakdown,
    Scope2SourceItem,
)


class CarbonService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.energy_repo = EnergyRepository(session)

    async def get_carbon_accounting(self, time_range: str = "month") -> CarbonAccountingResponse:
        scope1 = Scope1Breakdown(
            total_tons=4.18,
            target_tons=4.80,
            breakdown=[
                Scope1SourceItem(source="Natural Gas Thermal Furnace Burners", tons=3.42, share=81.8, activity_data="1,140 Nm³ gas consumed"),
                Scope1SourceItem(source="Diesel Backup Generator (Weekly Test Run)", tons=0.48, share=11.5, activity_data="180 Liters HSD fuel"),
                Scope1SourceItem(source="Facility Mobile Equipment & Forklifts", tons=0.28, share=6.7, activity_data="94 kg LPG"),
            ]
        )

        scope2 = Scope2Breakdown(
            total_tons=10.0,
            grid_emission_factor_kg_per_kwh=settings.GRID_EMISSION_FACTOR_KG_KWH,
            purchased_mwh=13.01,
            renewable_offset_tons=3.12,
            breakdown=[
                Scope2SourceItem(source="State Grid Electricity (MSEDCL 33kV)", tons=10.67, share=77.4),
                Scope2SourceItem(source="Rooftop Solar PV Offset (Self-Generation)", tons=-3.12, share=-22.6),
                Scope2SourceItem(source="Transmission & Distribution Line Losses", tons=0.45, share=3.3),
            ]
        )

        monthly_trend = [
            CarbonTrendPoint(month="May 2026", scope1=138.0, scope2=342.0, net_total=480.0, target=510.0),
            CarbonTrendPoint(month="Jun 2026", scope1=134.0, scope2=334.0, net_total=468.0, target=500.0),
            CarbonTrendPoint(month="Jul 2026", scope1=131.0, scope2=326.0, net_total=457.0, target=490.0),
            CarbonTrendPoint(month="Aug 2026", scope1=128.0, scope2=320.0, net_total=448.0, target=480.0),
            CarbonTrendPoint(month="Sep 2026", scope1=122.0, scope2=312.0, net_total=434.0, target=470.0),
            CarbonTrendPoint(month="Oct 2026 (MTD)", scope1=98.0, scope2=250.0, net_total=348.0, target=460.0),
        ]

        by_machine = [
            CarbonByMachinePoint(machine="Heat Furnace", carbon_tons=5.95, intensity_kg_per_unit=4.02, percent=42.0),
            CarbonByMachinePoint(machine="Air Compressor", carbon_tons=3.42, intensity_kg_per_unit=2.31, percent=24.1),
            CarbonByMachinePoint(machine="Assembly Line", carbon_tons=2.15, intensity_kg_per_unit=1.45, percent=15.2),
            CarbonByMachinePoint(machine="CNC Machine", carbon_tons=1.13, intensity_kg_per_unit=0.76, percent=8.0),
            CarbonByMachinePoint(machine="Cooling Pump", carbon_tons=0.85, intensity_kg_per_unit=0.57, percent=6.0),
            CarbonByMachinePoint(machine="Paint Booth", carbon_tons=0.68, intensity_kg_per_unit=0.46, percent=4.7),
        ]

        by_department = [
            CarbonByDepartmentPoint(department="Thermal Processing", tons=6.45, share_percent=45.5),
            CarbonByDepartmentPoint(department="Utilities Block", tons=4.27, share_percent=30.1),
            CarbonByDepartmentPoint(department="Final Assembly", tons=2.15, share_percent=15.2),
            CarbonByDepartmentPoint(department="Machining Hall", tons=1.13, share_percent=8.0),
            CarbonByDepartmentPoint(department="Finishing Line", tons=0.18, share_percent=1.2),
        ]

        esg_overview = EsgOverviewSchema(
            environmental_index=91.2,
            renewable_energy_share_percent=22.4,
            water_recycle_ratio_percent=74.8,
            waste_diverted_percent=92.6,
            gri_compliance="GRI 302 & 305 Full Assurance",
            brsr_status="SEBI BRSR Core Ready",
        )

        return CarbonAccountingResponse(
            today_total_tons=14.18,
            today_target_tons=16.50,
            month_to_date_tons=348.60,
            sustainability_score=88,
            sustainability_tier="Leader (Tier A+)",
            scope1=scope1,
            scope2=scope2,
            monthly_trend=monthly_trend,
            by_machine=by_machine,
            by_department=by_department,
            esg_overview=esg_overview,
        )
