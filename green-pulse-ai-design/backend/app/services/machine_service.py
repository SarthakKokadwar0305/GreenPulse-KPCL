"""
GreenPulse AI - Machine Service
Supplies full cyber-physical Digital Twin telemetry, 3-phase balance, and failure probability.
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.machine_repository import MachineRepository
from app.schemas.machine import (
    MachineDetailSchema,
    MachineInsightSchema,
    MachineTimelineState,
    MaintenanceRecordSchema,
    PhaseCurrent,
    VoltageBalance,
)


class MachineService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.machine_repo = MachineRepository(session)

    async def get_machines(
        self,
        zone: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[MachineDetailSchema]:
        """Returns all machine digital twins with optional zone and status filtering."""
        all_machines = await self.list_digital_twin_machines()
        filtered = all_machines
        if zone and zone != "all":
            filtered = [m for m in filtered if zone.lower() in m.zone.lower()]
        if status and status != "all":
            filtered = [m for m in filtered if m.status.lower() == status.lower()]
        return filtered

    async def list_digital_twin_machines(self) -> List[MachineDetailSchema]:
        """
        Returns all six flagship machines with color statuses:
        Green = Healthy (running)
        Yellow = Warning
        Red = Fault
        Blue = Idle
        """
        machines_data = [
            MachineDetailSchema(
                id="air-compressor",
                name="Air Compressor 01 (Lead)",
                code="COMP-01",
                category="Pneumatic Utilities",
                zone="Utilities Block A",
                status="warning",  # Yellow
                power_kw=412.0,
                rated_power_kw=500.0,
                temperature_c=86.0,
                thermal_threshold_c=90.0,
                voltage=VoltageBalance(l1=232.0, l2=230.0, l3=229.0, line_to_line=401.0, unbalance_percent=0.8),
                current=PhaseCurrent(l1=595.0, l2=591.0, l3=602.0),
                power_factor=0.88,
                runtime_hours_total=14820.0,
                runtime_hours_shift=7.4,
                mtbf_hours=740.0,
                mttr_hours=2.1,
                health_score=71,
                degradation_rate_percent=4.2,
                failure_probability_72h=28.5,
                likely_failure_mode="Stage-2 Unloader Valve Diaphragm Fatigue",
                carbon_kg_per_hour=337.8,
                carbon_today_kg=2804.0,
                carbon_share_percent=24.2,
                energy_today_kwh=3420.0,
                last_maintenance_date="12 Oct 2026",
                next_scheduled_pm="02 Nov 2026",
                maintenance_history=[
                    MaintenanceRecordSchema(date="12 Oct 2026", type="Oil & Filter Replacement", technician="R. Kulkarni", notes="Replaced synthetic lube ISO VG 46; inspected separator cartridge."),
                    MaintenanceRecordSchema(date="18 Aug 2026", type="Coupling Alignment", technician="D. Joshi", notes="Laser alignment within 0.03mm tolerance; vibration dampened."),
                ],
                ai_insight=MachineInsightSchema(
                    title="Stage-2 Unloader Valve Degradation",
                    explanation="Idle power consumption has risen from 58 kW to 84 kW during unload intervals over the last 14 operating days. Acoustic ultrasound telemetry shows continuous micro-leakage around valve seat.",
                    severity="warning",
                    suggested_remedy="Replace internal valve kit during planned break. Expected power recovery: 26 kW in idle mode.",
                    potential_savings_kw=26.0,
                ),
                timeline_24h=[
                    MachineTimelineState(time="00:00", state="running", power=380.0),
                    MachineTimelineState(time="04:00", state="running", power=410.0),
                    MachineTimelineState(time="06:00", state="idle", power=82.0),
                    MachineTimelineState(time="08:00", state="warning", power=445.0),
                    MachineTimelineState(time="12:00", state="warning", power=420.0),
                    MachineTimelineState(time="14:00", state="warning", power=412.0),
                ],
                specs={
                    "model": "Atlas Copco GA-355 VSD+",
                    "serial": "AC-2022-94812",
                    "commission_date": "15 Mar 2022",
                    "operator_in_charge": "K. Patil (Shift B)",
                    "electrical_substation": "Feeder 11kV Substation Bay 1",
                }
            ),
            MachineDetailSchema(
                id="comp-02",
                name="Air Compressor 02 (Trim)",
                code="COMP-02",
                category="Pneumatic Utilities",
                zone="Utilities Block A",
                status="running",
                power_kw=18.13,
                rated_power_kw=58.0,
                temperature_c=72.0,
                thermal_threshold_c=95.0,
                voltage=VoltageBalance(l1=231.0, l2=231.0, l3=230.0, line_to_line=400.0, unbalance_percent=0.4),
                current=PhaseCurrent(l1=31.2, l2=30.9, l3=31.4),
                power_factor=0.95,
                runtime_hours_total=11200.0,
                runtime_hours_shift=6.8,
                mtbf_hours=920.0,
                mttr_hours=1.8,
                health_score=92,
                degradation_rate_percent=1.2,
                failure_probability_72h=5.4,
                likely_failure_mode="None detected (VSD inverter harmonics nominal)",
                carbon_kg_per_hour=14.8,
                carbon_today_kg=122.0,
                carbon_share_percent=8.2,
                energy_today_kwh=145.0,
                last_maintenance_date="18 Sep 2026",
                next_scheduled_pm="18 Nov 2026",
                maintenance_history=[
                    MaintenanceRecordSchema(date="18 Sep 2026", type="VSD Drive Firmware Update", technician="Atlas Copco OEM", notes="Updated VSD inverter modulation curve; filter differential 0.12 bar."),
                ],
                ai_insight=MachineInsightSchema(
                    title="Trim Compressor Load Matching",
                    explanation="VSD modulation smoothly matches fluctuations in tooling air demand, maintaining header pressure at 7.0 bar.",
                    severity="success",
                    suggested_remedy="Maintain lead/lag sequence with Compressor 01.",
                    potential_savings_kw=0.0,
                ),
                timeline_24h=[
                    MachineTimelineState(time="00:00", state="running", power=16.0),
                    MachineTimelineState(time="06:00", state="running", power=18.5),
                    MachineTimelineState(time="12:00", state="running", power=19.2),
                    MachineTimelineState(time="18:00", state="running", power=17.8),
                ],
                specs={
                    "model": "Ingersoll Rand R55i VSD",
                    "serial": "IR-2022-6411",
                    "commission_date": "14 May 2022",
                    "operator_in_charge": "K. Patil (Shift B)",
                    "electrical_substation": "Feeder 11kV Substation Bay 1",
                }
            ),
            MachineDetailSchema(
                id="cnc-machine",
                name="CNC Machine 01",
                code="CNC-01",
                category="Precision Milling",
                zone="Precision Machining Bay 1",
                status="running",  # Green
                power_kw=5.96,
                rated_power_kw=22.0,
                temperature_c=42.0,
                thermal_threshold_c=65.0,
                voltage=VoltageBalance(l1=230.0, l2=231.0, l3=230.0, line_to_line=400.0, unbalance_percent=0.2),
                current=PhaseCurrent(l1=10.2, l2=10.1, l3=10.2),
                power_factor=0.94,
                runtime_hours_total=9820.0,
                runtime_hours_shift=7.2,
                mtbf_hours=1420.0,
                mttr_hours=1.2,
                health_score=96,
                degradation_rate_percent=0.8,
                failure_probability_72h=3.2,
                likely_failure_mode="None detected (Spindle harmonics nominal)",
                carbon_kg_per_hour=4.9,
                carbon_today_kg=40.0,
                carbon_share_percent=5.8,
                energy_today_kwh=48.0,
                last_maintenance_date="24 Oct 2026",
                next_scheduled_pm="24 Nov 2026",
                maintenance_history=[
                    MaintenanceRecordSchema(date="24 Oct 2026", type="Spindle Taper Cleaning", technician="P. Nair", notes="Runout verified under 2 microns; spindle chilled coolant refreshed."),
                ],
                ai_insight=MachineInsightSchema(
                    title="Optimal Toolpath Power Efficiency",
                    explanation="High-efficiency roughing adaptive trochoidal toolpaths are operating within 92-95% efficiency sweet spot.",
                    severity="success",
                    suggested_remedy="Maintain current spindle speed and high-pressure coolant pressure (70 bar).",
                    potential_savings_kw=0.0,
                ),
                timeline_24h=[
                    MachineTimelineState(time="00:00", state="idle", power=1.25),
                    MachineTimelineState(time="06:00", state="running", power=5.8),
                    MachineTimelineState(time="10:00", state="running", power=6.2),
                    MachineTimelineState(time="14:00", state="running", power=5.9),
                ],
                specs={
                    "model": "DMG Mori DMU 65 monoBLOCK",
                    "serial": "DMG-2023-4510",
                    "commission_date": "10 Jan 2023",
                    "operator_in_charge": "S. Gokhale (Shift B)",
                    "electrical_substation": "Feeder 415V MCC-2 Hall 2",
                }
            ),
            MachineDetailSchema(
                id="cnc-02",
                name="CNC Lathe 02",
                code="CNC-02",
                category="Precision Turning",
                zone="Precision Machining Bay 2",
                status="running",
                power_kw=4.79,
                rated_power_kw=18.0,
                temperature_c=39.0,
                thermal_threshold_c=62.0,
                voltage=VoltageBalance(l1=230.0, l2=230.0, l3=230.0, line_to_line=400.0, unbalance_percent=0.1),
                current=PhaseCurrent(l1=8.2, l2=8.3, l3=8.1),
                power_factor=0.93,
                runtime_hours_total=8450.0,
                runtime_hours_shift=6.9,
                mtbf_hours=1350.0,
                mttr_hours=1.4,
                health_score=94,
                degradation_rate_percent=0.9,
                failure_probability_72h=3.8,
                likely_failure_mode="None detected (Turret index indexing nominal)",
                carbon_kg_per_hour=3.9,
                carbon_today_kg=32.0,
                carbon_share_percent=4.6,
                energy_today_kwh=38.0,
                last_maintenance_date="15 Oct 2026",
                next_scheduled_pm="15 Nov 2026",
                maintenance_history=[
                    MaintenanceRecordSchema(date="15 Oct 2026", type="Chuck Hydraulic Pressure Check", technician="P. Nair", notes="Hydraulic chuck gripping pressure calibrated to 28 bar."),
                ],
                ai_insight=MachineInsightSchema(
                    title="Shaft Turning Energy Baseline",
                    explanation="Continuous OD turning cycle energy consumption matches baseline expectations within 2.1%.",
                    severity="success",
                    suggested_remedy="Continue current insert carbide grade.",
                    potential_savings_kw=0.0,
                ),
                timeline_24h=[
                    MachineTimelineState(time="00:00", state="idle", power=1.1),
                    MachineTimelineState(time="06:00", state="running", power=4.8),
                    MachineTimelineState(time="12:00", state="running", power=5.1),
                    MachineTimelineState(time="18:00", state="running", power=4.7),
                ],
                specs={
                    "model": "Doosan Puma 2600SY II",
                    "serial": "DSN-2023-1182",
                    "commission_date": "20 Mar 2023",
                    "operator_in_charge": "S. Gokhale (Shift B)",
                    "electrical_substation": "Feeder 415V MCC-2 Hall 2",
                }
            ),
            MachineDetailSchema(
                id="heat-furnace",
                name="Heat Furnace 01",
                code="FURN-01",
                category="Thermal Heat Treatment",
                zone="Thermal Processing Hall",
                status="running",  # Green
                power_kw=27.34,
                rated_power_kw=95.0,
                temperature_c=842.0,
                thermal_threshold_c=920.0,
                voltage=VoltageBalance(l1=231.0, l2=230.0, l3=232.0, line_to_line=402.0, unbalance_percent=0.4),
                current=PhaseCurrent(l1=982.0, l2=978.0, l3=985.0),
                power_factor=0.96,
                runtime_hours_total=21400.0,
                runtime_hours_shift=9.4,
                mtbf_hours=920.0,
                mttr_hours=3.8,
                health_score=84,
                degradation_rate_percent=1.9,
                failure_probability_72h=9.1,
                likely_failure_mode="Zone 3 Heating Element Oxidation",
                carbon_kg_per_hour=557.6,
                carbon_today_kg=4354.0,
                carbon_share_percent=37.5,
                energy_today_kwh=5310.0,
                last_maintenance_date="28 Sep 2026",
                next_scheduled_pm="15 Nov 2026",
                maintenance_history=[
                    MaintenanceRecordSchema(date="28 Sep 2026", type="Refractory Thermal Scan", technician="M. Deshmukh", notes="Repacked fiber blanket around door seal perimeter."),
                ],
                ai_insight=MachineInsightSchema(
                    title="Thermal Insulation Optimization Opportunity",
                    explanation="Skin temperature on upper door seal is 54°C (baseline 42°C), dissipating radiant loss.",
                    severity="info",
                    suggested_remedy="Tighten pneumatic clamp cylinder and shift batch ramp to 22:00 off-peak slot.",
                    potential_savings_kw=14.0,
                ),
                timeline_24h=[
                    MachineTimelineState(time="00:00", state="running", power=620.0),
                    MachineTimelineState(time="08:00", state="running", power=680.0),
                    MachineTimelineState(time="14:00", state="running", power=680.0),
                ],
                specs={
                    "model": "Ipsen Vacuum TurboTreater 400",
                    "serial": "IPS-2021-38290",
                    "commission_date": "20 Nov 2021",
                    "operator_in_charge": "A. Shinde (Shift B)",
                    "electrical_substation": "Feeder 11kV Substation Bay 2",
                }
            ),
            MachineDetailSchema(
                id="hvac-01",
                name="Central HVAC Chiller 01",
                code="HVAC-01",
                category="Environmental Control",
                zone="Central Chiller Plant",
                status="running",
                power_kw=10.22,
                rated_power_kw=15.0,
                temperature_c=14.0,
                thermal_threshold_c=25.0,
                voltage=VoltageBalance(l1=230.0, l2=231.0, l3=230.0, line_to_line=400.0, unbalance_percent=0.2),
                current=PhaseCurrent(l1=17.5, l2=17.4, l3=17.6),
                power_factor=0.92,
                runtime_hours_total=16400.0,
                runtime_hours_shift=8.0,
                mtbf_hours=1200.0,
                mttr_hours=1.5,
                health_score=88,
                degradation_rate_percent=1.4,
                failure_probability_72h=4.1,
                likely_failure_mode="Chilled water delta-T low bypass",
                carbon_kg_per_hour=8.38,
                carbon_today_kg=67.0,
                carbon_share_percent=4.8,
                energy_today_kwh=81.8,
                last_maintenance_date="05 Oct 2026",
                next_scheduled_pm="05 Dec 2026",
                maintenance_history=[
                    MaintenanceRecordSchema(date="05 Oct 2026", type="Refrigerant Level Check", technician="Johnson Controls", notes="R-134a pressure 4.2 bar; condenser tubes descaled."),
                ],
                ai_insight=MachineInsightSchema(
                    title="Chilled Water Temperature Optimization",
                    explanation="Supply temperature of 14°C maintains precision machining tolerances while saving 12% chiller power.",
                    severity="success",
                    suggested_remedy="Maintain economizer mode during cool night shifts.",
                    potential_savings_kw=1.8,
                ),
                timeline_24h=[
                    MachineTimelineState(time="00:00", state="running", power=9.8),
                    MachineTimelineState(time="06:00", state="running", power=10.5),
                    MachineTimelineState(time="12:00", state="running", power=11.2),
                    MachineTimelineState(time="18:00", state="running", power=10.1),
                ],
                specs={
                    "model": "Daikin Pathfinder AWV 15",
                    "serial": "DKN-2021-3320",
                    "commission_date": "18 Aug 2021",
                    "operator_in_charge": "M. Banerjee (Shift B)",
                    "electrical_substation": "Feeder 415V Utilities MCC-1",
                }
            ),
            MachineDetailSchema(
                id="paint-booth",
                name="Paint Booth",
                code="PAINT-01",
                category="Surface Finishing",
                zone="Finishing Line",
                status="idle",  # Blue
                power_kw=36.0,
                rated_power_kw=210.0,
                temperature_c=27.0,
                thermal_threshold_c=45.0,
                voltage=VoltageBalance(l1=230.0, l2=230.0, l3=231.0, line_to_line=400.0, unbalance_percent=0.2),
                current=PhaseCurrent(l1=52.0, l2=52.0, l3=53.0),
                power_factor=0.72,
                runtime_hours_total=7650.0,
                runtime_hours_shift=0.0,
                mtbf_hours=1100.0,
                mttr_hours=1.5,
                health_score=90,
                degradation_rate_percent=1.1,
                failure_probability_72h=4.5,
                likely_failure_mode="Exhaust Filter Saturation",
                carbon_kg_per_hour=29.5,
                carbon_today_kg=442.0,
                carbon_share_percent=3.8,
                energy_today_kwh=540.0,
                last_maintenance_date="15 Oct 2026",
                next_scheduled_pm="15 Nov 2026",
                maintenance_history=[
                    MaintenanceRecordSchema(date="15 Oct 2026", type="Filter Replacement", technician="CleanAir Tech", notes="Ceiling HEPA filters refreshed."),
                ],
                ai_insight=MachineInsightSchema(
                    title="Idling Airflow Power Drain Detected",
                    explanation="Booth blowers drawing 36 kW continuously while no chassis has passed sensor.",
                    severity="warning",
                    suggested_remedy="Engage automated setback: throttle blowers to 25% after 10 mins inactivity.",
                    potential_savings_kw=27.0,
                ),
                timeline_24h=[
                    MachineTimelineState(time="00:00", state="running", power=178.0),
                    MachineTimelineState(time="08:00", state="idle", power=36.0),
                    MachineTimelineState(time="14:00", state="idle", power=36.0),
                ],
                specs={
                    "model": "Dürr EcoDryScrubber Booth",
                    "serial": "DURR-2022-1082",
                    "commission_date": "04 Aug 2022",
                    "operator_in_charge": "V. Jadhav (Shift B)",
                    "electrical_substation": "Feeder 415V Finishing MCC",
                }
            ),
            MachineDetailSchema(
                id="cooling-pump",
                name="Cooling Pump 01",
                code="PUMP-01",
                category="Hydronic Circulation",
                zone="Utilities Block B",
                status="running",  # Green
                power_kw=3.74,
                rated_power_kw=12.0,
                temperature_c=38.0,
                thermal_threshold_c=55.0,
                voltage=VoltageBalance(l1=229.0, l2=230.0, l3=231.0, line_to_line=399.0, unbalance_percent=0.4),
                current=PhaseCurrent(l1=6.5, l2=6.4, l3=6.5),
                power_factor=0.89,
                runtime_hours_total=18900.0,
                runtime_hours_shift=9.8,
                mtbf_hours=890.0,
                mttr_hours=1.4,
                health_score=95,
                degradation_rate_percent=1.2,
                failure_probability_72h=4.8,
                likely_failure_mode="Suction Strainer Differential Pressure Drop",
                carbon_kg_per_hour=3.06,
                carbon_today_kg=25.0,
                carbon_share_percent=3.2,
                energy_today_kwh=31.2,
                last_maintenance_date="04 Oct 2026",
                next_scheduled_pm="04 Nov 2026",
                maintenance_history=[
                    MaintenanceRecordSchema(date="04 Oct 2026", type="Mechanical Seal Flush", technician="R. Kulkarni", notes="Burgmann seal nominal."),
                ],
                ai_insight=MachineInsightSchema(
                    title="Cooling Pump Flow Throttling Inefficiency",
                    explanation="Discharge butterfly valve throttled to 68%, dissipating friction loss.",
                    severity="info",
                    suggested_remedy="Modulate VFD inverter to 44.5 Hz and open butterfly valve to 100% full bore.",
                    potential_savings_kw=1.2,
                ),
                timeline_24h=[
                    MachineTimelineState(time="00:00", state="running", power=3.7),
                    MachineTimelineState(time="08:00", state="running", power=3.8),
                    MachineTimelineState(time="14:00", state="running", power=3.7),
                ],
                specs={
                    "model": "Grundfos CR 64-3 Industrial",
                    "serial": "GF-PMP-1102",
                    "commission_date": "18 Sep 2021",
                    "operator_in_charge": "K. Patil (Shift B)",
                    "electrical_substation": "Feeder 415V Utilities MCC-1",
                }
            ),
            MachineDetailSchema(
                id="assembly-line",
                name="Assembly Line 01",
                code="ASSY-01",
                category="Robotic Assembly",
                zone="Final Assembly",
                status="running",  # Green
                power_kw=236.0,
                rated_power_kw=280.0,
                temperature_c=41.0,
                thermal_threshold_c=60.0,
                voltage=VoltageBalance(l1=231.0, l2=231.0, l3=230.0, line_to_line=401.0, unbalance_percent=0.2),
                current=PhaseCurrent(l1=341.0, l2=339.0, l3=342.0),
                power_factor=0.95,
                runtime_hours_total=12400.0,
                runtime_hours_shift=9.9,
                mtbf_hours=1850.0,
                mttr_hours=0.9,
                health_score=98,
                degradation_rate_percent=0.4,
                failure_probability_72h=1.2,
                likely_failure_mode="None (Full servo synchronization verified)",
                carbon_kg_per_hour=193.5,
                carbon_today_kg=1763.0,
                carbon_share_percent=15.2,
                energy_today_kwh=2150.0,
                last_maintenance_date="09 Oct 2026",
                next_scheduled_pm="09 Dec 2026",
                maintenance_history=[
                    MaintenanceRecordSchema(date="09 Oct 2026", type="6-Axis Servo Calibration", technician="Kuka Certified", notes="Mastering calibration verified."),
                ],
                ai_insight=MachineInsightSchema(
                    title="Regenerative Braking Optimization",
                    explanation="Robotic joint deceleration energy returns 18 kW into DC bus.",
                    severity="success",
                    suggested_remedy="Continue coordinated deceleration smoothing profile.",
                    potential_savings_kw=0.0,
                ),
                timeline_24h=[
                    MachineTimelineState(time="00:00", state="running", power=224.0),
                    MachineTimelineState(time="08:00", state="running", power=240.0),
                    MachineTimelineState(time="14:00", state="running", power=236.0),
                ],
                specs={
                    "model": "Kuka FlexLine Cell-8X",
                    "serial": "KUKA-2023-8821",
                    "commission_date": "22 Feb 2023",
                    "operator_in_charge": "N. Joshi (Shift B)",
                    "electrical_substation": "Feeder 415V Assembly Busduct",
                }
            ),
        ]
        return machines_data

    async def get_machine_by_id(self, machine_id: str) -> Optional[MachineDetailSchema]:
        machines = await self.list_digital_twin_machines()
        mid_clean = machine_id.lower().replace("_", "-").strip()
        mid_norm = mid_clean.replace("comp", "cmp").replace("furn", "frn").replace("paint", "pnt").replace("pump", "pmp").replace("-", "")
        for m in machines:
            m_code_norm = m.code.lower().replace("comp", "cmp").replace("furn", "frn").replace("paint", "pnt").replace("pump", "pmp").replace("-", "")
            m_id_norm = m.id.lower().replace("comp", "cmp").replace("furn", "frn").replace("paint", "pnt").replace("pump", "pmp").replace("-", "")
            if (m.id.lower() == mid_clean or 
                m.code.lower() == mid_clean or
                m_id_norm == mid_norm or 
                m_code_norm == mid_norm or
                mid_clean in m.name.lower()):
                return m
        return None
