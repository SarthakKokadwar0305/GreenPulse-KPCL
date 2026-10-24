"""
GreenPulse AI - Plant Service
Manages plant executive summaries, department loads, shift information, and utility metrics.
"""
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.repositories.machine_repository import MachineRepository
from app.schemas.plant import (
    ActiveUtilityAssetSchema,
    DepartmentOverviewSchema,
    FactoryTimelineEventSchema,
    HourlyThroughputPoint,
    PlantOverviewResponse,
    ProductionSummarySchema,
    ShiftInformationSchema,
    UtilityConsumptionSchema,
)


class PlantService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.machine_repo = MachineRepository(session)

    async def get_plant_overview(self) -> PlantOverviewResponse:
        production_summary = ProductionSummarySchema(
            target_units=1600,
            actual_units=1482,
            throughput_rate_per_hour=185,
            first_pass_yield=98.6,
            downtime_minutes=18,
            active_lines=5,
            total_lines=5,
            hourly_throughput=[
                HourlyThroughputPoint(hour="06:00", target=180, actual=172),
                HourlyThroughputPoint(hour="07:00", target=190, actual=188),
                HourlyThroughputPoint(hour="08:00", target=200, actual=195),
                HourlyThroughputPoint(hour="09:00", target=200, actual=198),
                HourlyThroughputPoint(hour="10:00", target=200, actual=202),
                HourlyThroughputPoint(hour="11:00", target=190, actual=189),
                HourlyThroughputPoint(hour="12:00", target=180, actual=174),
                HourlyThroughputPoint(hour="13:00", target=200, actual=196),
            ]
        )

        departments = [
            DepartmentOverviewSchema(
                id="dept-thermal",
                name="Thermal Processing",
                zone="Bay 3",
                power_kw=680.0,
                energy_today_kwh=5310.0,
                efficiency=84.0,
                health_score=84,
                status="normal",
                machine_count=3,
            ),
            DepartmentOverviewSchema(
                id="dept-utilities",
                name="Central Utilities Block",
                zone="Block A & B",
                power_kw=486.0,
                energy_today_kwh=4030.0,
                efficiency=79.0,
                health_score=75,
                status="warning",
                machine_count=4,
            ),
            DepartmentOverviewSchema(
                id="dept-assembly",
                name="Final Assembly & Robotics",
                zone="Hall 1",
                power_kw=236.0,
                energy_today_kwh=2150.0,
                efficiency=96.0,
                health_score=98,
                status="optimal",
                machine_count=6,
            ),
            DepartmentOverviewSchema(
                id="dept-machining",
                name="Precision CNC Machining",
                zone="Hall 2",
                power_kw=118.0,
                energy_today_kwh=980.0,
                efficiency=93.0,
                health_score=94,
                status="optimal",
                machine_count=5,
            ),
            DepartmentOverviewSchema(
                id="dept-finishing",
                name="Finishing & Coating Bay",
                zone="Bay 4",
                power_kw=36.0,
                energy_today_kwh=540.0,
                efficiency=52.0,
                health_score=90,
                status="normal",
                machine_count=2,
            ),
        ]

        utilities = [
            UtilityConsumptionSchema(
                id="util-electric",
                name="Main Electrical Feed (33kV)",
                current_rate=1556.0,
                unit="kW",
                capacity=2500.0,
                utilization_percent=62.2,
                today_total=13010.0,
                status="normal",
            ),
            UtilityConsumptionSchema(
                id="util-air",
                name="Compressed Air Ring (6.8 bar)",
                current_rate=42.5,
                unit="Nm³/min",
                capacity=60.0,
                utilization_percent=70.8,
                today_total=398.0,
                status="peak",
            ),
            UtilityConsumptionSchema(
                id="util-water",
                name="Process Cooling Water Loop",
                current_rate=14.2,
                unit="m³/h",
                capacity=25.0,
                utilization_percent=56.8,
                today_total=128.0,
                status="normal",
            ),
            UtilityConsumptionSchema(
                id="util-gas",
                name="Natural Gas Fuel Feed",
                current_rate=48.0,
                unit="Nm³/h",
                capacity=80.0,
                utilization_percent=60.0,
                today_total=412.0,
                status="normal",
            ),
        ]

        active_utilities = [
            ActiveUtilityAssetSchema(
                id="u-01",
                name="Rotary Screw Air Compressor A-01",
                type="Compressed Air",
                power_kw=412.0,
                load_factor=82.4,
                status="warning",
                runtime_today_hours=9.2,
            ),
            ActiveUtilityAssetSchema(
                id="u-02",
                name="Centrifugal Cooling Tower Pump P-102",
                type="Hydronic Cooling",
                power_kw=74.0,
                load_factor=67.3,
                status="running",
                runtime_today_hours=9.8,
            ),
            ActiveUtilityAssetSchema(
                id="u-03",
                name="Substation Main Transformer TR-01",
                type="Power Distribution",
                power_kw=840.0,
                load_factor=56.0,
                status="running",
                runtime_today_hours=24.0,
            ),
            ActiveUtilityAssetSchema(
                id="u-04",
                name="Substation Auxiliary Transformer TR-02",
                type="Power Distribution",
                power_kw=716.0,
                load_factor=47.7,
                status="running",
                runtime_today_hours=24.0,
            ),
        ]

        shift_info = ShiftInformationSchema(
            current_shift="Shift B (Afternoon Production)",
            shift_code="SH-B",
            time_range="14:00 - 22:00",
            lead_engineer="Elena Vance, CEM",
            lead_role="Lead Shift Engineer & Certified Energy Auditor",
            operators_on_floor=38,
            maintenance_techs=4,
            shift_energy_budget_kwh=12500.0,
            shift_energy_consumed_kwh=8140.0,
            production_target=1600,
            production_actual=1482,
            elapsed_percent=68,
        )

        timeline = [
            FactoryTimelineEventSchema(
                id="t-1",
                time="14:00",
                title="Shift B Handover & Initial Meter Synchronization",
                category="production",
                description="Shift change completed with clean log. Peak demand baseline locked at 1,510 kW.",
                severity="info",
            ),
            FactoryTimelineEventSchema(
                id="t-2",
                time="14:45",
                title="Heat Furnace Batch Annealing Cycle #2 Initiated",
                category="production",
                description="Ramp to 850°C completed in 28 mins; power stabilized at 680 kW.",
                severity="info",
            ),
            FactoryTimelineEventSchema(
                id="t-3",
                time="15:20",
                title="Air Compressor Stage-2 Valve Leakage Alert Triggered",
                category="maintenance",
                description="Unload power elevated by 24 kW above normal idle baseline. Assigned to shift tech.",
                severity="warning",
            ),
            FactoryTimelineEventSchema(
                id="t-4",
                time="16:15",
                title="Rooftop Solar PV Inverter Peak Output (342 kW)",
                category="grid",
                description="Solar generation supplied 22.4% of total instantaneous plant demand.",
                severity="success",
            ),
        ]

        health_summary = {
            "health_index": 91.4,
            "predictive_risk": 8.6,
            "uptime_percent": 99.1,
            "compliance_status": "GRI 302/305 Compliant",
            "iso50001_status": "Certified (Audit Valid through May 2027)",
        }

        return PlantOverviewResponse(
            plant_id=settings.PLANT_CODE,
            plant_name=settings.PLANT_NAME,
            last_updated=datetime.now(timezone.utc).isoformat(),
            production_summary=production_summary,
            departments=departments,
            utilities=utilities,
            active_utilities=active_utilities,
            shift_info=shift_info,
            timeline=timeline,
            health_summary=health_summary,
        )
