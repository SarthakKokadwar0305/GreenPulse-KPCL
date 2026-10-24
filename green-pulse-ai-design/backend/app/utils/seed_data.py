"""
GreenPulse AI - Production Database Seeder
Seeds full asset master data, historical energy telemetry from datasets,
production efficiency, carbon accounting, anomalies, and recommendations.
Synchronized 100% with greenpulse_dataset and machine_config.py.
"""
from datetime import datetime, date, timedelta, timezone
from pathlib import Path
import pandas as pd
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.core.security import hash_password
from app.models.auth import Role, Permission
from app.models.user import User
from app.models.machine import Machine
from app.models.energy import EnergyReading
from app.models.carbon import CarbonEmission
from app.models.production import Production
from app.models.anomaly import Anomaly
from app.models.recommendation import Recommendation
from app.models.report import Report
from app.models.maintenance import MaintenanceHistory

DATASETS_DIR = Path(__file__).resolve().parent.parent.parent / "datasets"

# Master Fleet Definition matching services/config/machine_config.py & dataset
FLEET_SPECIFICATIONS = [
    {
        "id": "cnc-01",
        "code": "CNC-01",
        "name": "5-Axis High Precision CNC Milling Center",
        "short_name": "CNC Mill 01",
        "process_type": "CNC Machining",
        "zone": "Precision Machining Bay 1",
        "icon_key": "cog",
        "rated_power_kw": 22.0,
        "status": "running",
        "health_score": 96,
        "model_number": "DMG Mori DMU 65 monoBLOCK",
        "serial_number": "DMG-2023-4510",
    },
    {
        "id": "cnc-02",
        "code": "CNC-02",
        "name": "Heavy Duty 4-Axis CNC Lathe",
        "short_name": "CNC Lathe 02",
        "process_type": "CNC Machining",
        "zone": "Precision Machining Bay 2",
        "icon_key": "cog",
        "rated_power_kw": 18.0,
        "status": "running",
        "health_score": 94,
        "model_number": "Doosan Puma 2600SY II",
        "serial_number": "DSN-2023-1182",
    },
    {
        "id": "comp-01",
        "code": "COMP-01",
        "name": "Rotary Screw Industrial Air Compressor #1 (Lead)",
        "short_name": "Air Compressor 01",
        "process_type": "Compressed Air Supply",
        "zone": "Utilities Block A",
        "icon_key": "wind",
        "rated_power_kw": 58.0,
        "status": "warning",
        "health_score": 71,
        "model_number": "Atlas Copco GA 75 VSD+",
        "serial_number": "AC-2024-9981",
    },
    {
        "id": "comp-02",
        "code": "COMP-02",
        "name": "Variable Speed Screw Compressor #2 (Trim/Lag)",
        "short_name": "Air Compressor 02",
        "process_type": "Compressed Air Supply",
        "zone": "Utilities Block A",
        "icon_key": "wind",
        "rated_power_kw": 58.0,
        "status": "running",
        "health_score": 92,
        "model_number": "Ingersoll Rand R55i VSD",
        "serial_number": "IR-2022-6411",
    },
    {
        "id": "furn-01",
        "code": "FURN-01",
        "name": "Continuous Atmospheric Heat Treatment Annealing Furnace",
        "short_name": "Heat Furnace 01",
        "process_type": "Thermal Heat Treatment",
        "zone": "Thermal Processing Hall",
        "icon_key": "flame",
        "rated_power_kw": 95.0,
        "status": "running",
        "health_score": 84,
        "model_number": "Seco/Warwick Vector 2.0",
        "serial_number": "SW-VF-8812",
    },
    {
        "id": "hvac-01",
        "code": "HVAC-01",
        "name": "Central Water-Cooled HVAC Chiller & Air Handling Unit",
        "short_name": "HVAC Chiller 01",
        "process_type": "Ventilation HVAC",
        "zone": "Central Chiller Plant",
        "icon_key": "activity",
        "rated_power_kw": 15.0,
        "status": "running",
        "health_score": 88,
        "model_number": "Daikin Pathfinder AWV 15",
        "serial_number": "DKN-2021-3320",
    },
    {
        "id": "paint-01",
        "code": "PAINT-01",
        "name": "Downdraft Automated Paint Spray Booth & Drying Plenum",
        "short_name": "Paint Booth 01",
        "process_type": "Automated Surface Finishing",
        "zone": "Finishing Bay B",
        "icon_key": "brush",
        "rated_power_kw": 32.0,
        "status": "idle",
        "health_score": 90,
        "model_number": "Eisenmann E-Shuttle 200",
        "serial_number": "ES-2022-7721",
    },
    {
        "id": "pump-01",
        "code": "PUMP-01",
        "name": "High-Pressure Cutting Fluid & Coolant Recirculation Pump",
        "short_name": "Coolant Pump 01",
        "process_type": "Coolant Recirculation",
        "zone": "Utilities Block B",
        "icon_key": "activity",
        "rated_power_kw": 12.0,
        "status": "running",
        "health_score": 95,
        "model_number": "Grundfos CR 64-3 Industrial",
        "serial_number": "GF-PMP-1102",
    },
    {
        "id": "assy-01",
        "code": "ASSY-01",
        "name": "High-Speed Robotic Assembly Cell",
        "short_name": "Assembly Cell 01",
        "process_type": "Multi-Axis Robotic Assembly",
        "zone": "Final Assembly Hall",
        "icon_key": "layers",
        "rated_power_kw": 90.0,
        "status": "running",
        "health_score": 98,
        "model_number": "ABB IRB 6700 Cell",
        "serial_number": "ABB-R67-009",
    },
]


async def seed_database(session: AsyncSession) -> None:
    """Seeds master fleet, telemetry slices, production, carbon, and reports."""
    logger.info("Starting enterprise database seeding & synchronization...")

    # 1. Synchronize Machine Fleet (Ensure all 8 dataset machines + assembly cell exist)
    machine_stmt = select(Machine)
    existing_machines = (await session.execute(machine_stmt)).scalars().all()
    existing_codes = {m.code: m for m in existing_machines}

    for spec in FLEET_SPECIFICATIONS:
        code = spec["code"]
        if code not in existing_codes:
            m = Machine(
                id=spec["id"],
                code=spec["code"],
                name=spec["name"],
                short_name=spec["short_name"],
                process_type=spec["process_type"],
                zone=spec["zone"],
                icon_key=spec["icon_key"],
                rated_power_kw=spec["rated_power_kw"],
                status=spec["status"],
                health_score=spec["health_score"],
                model_number=spec["model_number"],
                serial_number=spec["serial_number"],
                is_active=True,
            )
            session.add(m)
            logger.info(f"Added missing machine: [{code}] {spec['name']}")
    await session.commit()

    # Re-fetch machine mapping
    current_machines = (await session.execute(select(Machine))).scalars().all()
    code_to_id = {m.code: m.id for m in current_machines}
    machine_by_id = {m.id: m for m in current_machines}
    machine_by_code = {m.code: m for m in current_machines}

    # Helper function to find machine by either ID or Code
    def find_machine(ident: str):
        if ident in machine_by_id:
            return machine_by_id[ident]
        if ident in machine_by_code:
            return machine_by_code[ident]
        for m in current_machines:
            if m.id.lower() == ident.lower() or m.code.lower() == ident.lower():
                return m
        return None

    # 2. Seed Granular Enterprise RBAC Permissions
    ALL_PERMISSIONS = [
        ("VIEW_DASHBOARD", "View Dashboard", "Access plant executive dashboard and KPIs", "dashboard"),
        ("VIEW_PLANT", "View Plant Overview", "Access full plant overview and all department breakdowns", "plant"),
        ("VIEW_MACHINE", "View Machine Fleet", "Access full machine fleet telemetry and digital twin", "machines"),
        ("VIEW_ASSIGNED_MACHINE", "View Assigned Machines", "Access operator assigned machines only", "machines"),
        ("VIEW_DIGITAL_TWIN", "View Digital Twin", "Inspect 3D digital twin telemetry profiles", "digital_twin"),
        ("VIEW_ENERGY", "View Energy Analytics", "Access energy explorer, load curves, and peak demand", "energy"),
        ("VIEW_CARBON", "View Carbon Accounting", "Access Scope 1 and Scope 2 GHG protocol analytics", "carbon"),
        ("VIEW_FORECAST", "View AI Forecasts", "Access multi-horizon demand forecasting and SHAP explanations", "forecast"),
        ("VIEW_ALERTS", "View Alerts & Anomalies", "Access real-time operational alerts and anomaly center", "alerts"),
        ("VIEW_RECOMMENDATIONS", "View Recommendations", "Access prescriptive energy conservation measures", "recommendations"),
        ("APPROVE_RECOMMENDATIONS", "Approve Recommendations", "Approve energy conservation actions and dispatch setpoints", "recommendations"),
        ("VIEW_SIMULATOR", "View What-If Simulator", "Access what-if parameter modeling dashboard", "simulator"),
        ("RUN_SIMULATION", "Run What-If Simulation", "Execute counterfactual load and tariff simulations", "simulator"),
        ("VIEW_REPORTS", "View Reports", "Access and review compliance audit reports", "reports"),
        ("EXPORT_REPORTS", "Export Reports", "Generate and export PDF/CSV energy compliance reports", "reports"),
        ("MANAGE_USERS", "Manage Users", "Register, update, and manage plant personnel accounts", "admin"),
        ("CONFIGURE_THRESHOLDS", "Configure Thresholds", "Modify industrial alert and baseline operational thresholds", "admin"),
        ("ACKNOWLEDGE_ALERT", "Acknowledge Alert", "Acknowledge active equipment alarms and anomalies", "alerts"),
        ("UPDATE_MACHINE_STATUS", "Update Machine Status", "Modify machine operational state (running, idle, maintenance)", "machines"),
        ("SCHEDULE_MAINTENANCE", "Schedule Maintenance", "Create work orders and schedule equipment servicing", "maintenance"),
        ("APPROVE_MAINTENANCE", "Approve Maintenance", "Sign off on preventive and corrective maintenance tickets", "maintenance"),
        ("VIEW_AUDIT_LOGS", "View Audit Logs", "Access immutable security and compliance audit logs", "security"),
    ]

    perm_objs = {}
    existing_perms = (await session.execute(select(Permission))).scalars().all()
    existing_perm_codes = {p.code: p for p in existing_perms}

    for code, name, desc_text, mod in ALL_PERMISSIONS:
        if code not in existing_perm_codes:
            p = Permission(code=code, name=name, description=desc_text, module=mod)
            session.add(p)
            perm_objs[code] = p
        else:
            perm_objs[code] = existing_perm_codes[code]
    await session.commit()

    # Re-query all permissions
    all_perm_db = (await session.execute(select(Permission))).scalars().all()
    perm_map = {p.code: p for p in all_perm_db}

    # 3. Seed Enterprise Roles & Permission Mappings
    ROLE_DEFINITIONS = [
        {
            "code": "PLANT_HEAD",
            "name": "Plant Head",
            "description": "Highest authority inside the company with full operational oversight.",
            "permissions": list(perm_map.keys()),  # Full access
        },
        {
            "code": "ENERGY_MANAGER",
            "name": "Energy Manager",
            "description": "Responsible for energy optimization, carbon reduction, and efficiency forecasting.",
            "permissions": [
                "VIEW_DASHBOARD", "VIEW_ENERGY", "VIEW_CARBON", "VIEW_FORECAST",
                "VIEW_RECOMMENDATIONS", "APPROVE_RECOMMENDATIONS",
                "VIEW_SIMULATOR", "RUN_SIMULATION", "VIEW_REPORTS", "EXPORT_REPORTS"
            ],
        },
        {
            "code": "MAINTENANCE_MANAGER",
            "name": "Maintenance Manager",
            "description": "Responsible for machine health, vibration monitoring, anomaly resolution, and maintenance scheduling.",
            "permissions": [
                "VIEW_DASHBOARD", "VIEW_MACHINE", "VIEW_DIGITAL_TWIN", "VIEW_ALERTS",
                "ACKNOWLEDGE_ALERT", "SCHEDULE_MAINTENANCE", "APPROVE_MAINTENANCE",
                "UPDATE_MACHINE_STATUS", "VIEW_RECOMMENDATIONS"
            ],
        },
        {
            "code": "OPERATOR",
            "name": "Operator",
            "description": "Responsible for operating assigned machinery safely and acknowledging active alarms.",
            "permissions": [
                "VIEW_DASHBOARD", "VIEW_ASSIGNED_MACHINE", "VIEW_DIGITAL_TWIN",
                "VIEW_ALERTS", "ACKNOWLEDGE_ALERT", "UPDATE_MACHINE_STATUS"
            ],
        },
    ]

    role_objs = {}
    from sqlalchemy.orm import selectinload
    existing_roles = (await session.execute(select(Role).options(selectinload(Role.permissions)))).scalars().all()
    existing_role_codes = {r.code: r for r in existing_roles}

    for r_def in ROLE_DEFINITIONS:
        r_code = r_def["code"]
        target_perms = [perm_map[p_code] for p_code in r_def["permissions"] if p_code in perm_map]
        if r_code not in existing_role_codes:
            role_entry = Role(code=r_code, name=r_def["name"], description=r_def["description"])
            role_entry.permissions = target_perms
            session.add(role_entry)
            role_objs[r_code] = role_entry
        else:
            role_entry = existing_role_codes[r_code]
            role_entry.permissions = target_perms
            role_objs[r_code] = role_entry
    await session.commit()

    # Re-query all roles with permissions
    all_role_db = (await session.execute(select(Role).options(selectinload(Role.permissions)))).scalars().all()
    role_map = {r.code: r for r in all_role_db}

    # 4. Seed the 4 Enterprise Role Personas + Admin
    ENTERPRISE_USERS = [
        {
            "username": "plant_head",
            "email": "plant.head@greenpulse.ai",
            "password": "PlantHead@2026",
            "full_name": "Rajesh Nair",
            "role": "PLANT_HEAD",
            "department": "Executive Plant Management",
            "is_admin": True,
            "assigned_ids": list(machine_by_id.keys()),
        },
        {
            "username": "energy_manager",
            "email": "energy.manager@greenpulse.ai",
            "password": "EnergyManager@2026",
            "full_name": "Vikram Patel",
            "role": "ENERGY_MANAGER",
            "department": "Energy & Sustainability",
            "is_admin": False,
            "assigned_ids": [],
        },
        {
            "username": "maintenance_manager",
            "email": "maintenance.manager@greenpulse.ai",
            "password": "Maintenance@2026",
            "full_name": "Suresh Rao",
            "role": "MAINTENANCE_MANAGER",
            "department": "Reliability & Maintenance Engineering",
            "is_admin": False,
            "assigned_ids": list(machine_by_id.keys()),
        },
        {
            "username": "operator_lead",
            "email": "operator1@greenpulse.ai",
            "password": "Operator@2026",
            "full_name": "Amit Shinde",
            "role": "OPERATOR",
            "department": "Machining Bay Operations",
            "is_admin": False,
            "assigned_ids": ["comp-01", "cnc-01"],
        },
        {
            "username": "admin",
            "email": "admin@greenpulse.ai",
            "password": "GreenPulse@2026",
            "full_name": "Plant Systems Administrator",
            "role": "PLANT_HEAD",
            "department": "Operations",
            "is_admin": True,
            "assigned_ids": list(machine_by_id.keys()),
        },
    ]

    for u_spec in ENTERPRISE_USERS:
        u_email = u_spec["email"]
        u_user = (await session.execute(
            select(User)
            .options(selectinload(User.roles), selectinload(User.assigned_machines))
            .where(User.email == u_email)
        )).scalar_one_or_none()

        assigned_objs = [find_machine(ident) for ident in u_spec["assigned_ids"]]
        assigned_objs = [m for m in assigned_objs if m is not None]
        target_role = role_map[u_spec["role"]]

        if not u_user:
            new_u = User(
                username=u_spec["username"],
                email=u_spec["email"],
                hashed_password=hash_password(u_spec["password"]),
                full_name=u_spec["full_name"],
                role=u_spec["role"],
                department=u_spec["department"],
                status="active",
                is_active=True,
                is_admin=u_spec["is_admin"],
            )
            new_u.roles.append(target_role)
            new_u.assigned_machines = assigned_objs
            session.add(new_u)
            logger.info(f"Seeded enterprise user [{u_spec['role']}] '{u_spec['username']}' ({u_spec['email']})")
        else:
            # Update credentials & associations to ensure synchronization
            u_user.username = u_spec["username"]
            u_user.full_name = u_spec["full_name"]
            u_user.role = u_spec["role"]
            u_user.department = u_spec["department"]
            u_user.is_admin = u_spec["is_admin"]
            u_user.hashed_password = hash_password(u_spec["password"])
            u_user.roles = [target_role]
            u_user.assigned_machines = assigned_objs
    await session.commit()

    # 3. Seed Production Records from production_efficiency_by_day.csv
    prod_stmt = select(Production)
    existing_prod_cnt = (await session.execute(select(Production))).scalars().all()
    prod_csv_path = DATASETS_DIR / "production_efficiency_by_day.csv"

    if len(existing_prod_cnt) == 0 and prod_csv_path.exists():
        logger.info("Seeding production records from dataset...")
        df_prod = pd.read_csv(prod_csv_path)
        records = []
        for _, row in df_prod.iterrows():
            m_code = row["machine_id"]
            if m_code in code_to_id:
                p_date = datetime.strptime(str(row["local_date"]), "%Y-%m-%d").date()
                good_units = int(row.get("good_units", 0))
                units_produced = int(row.get("units_produced", good_units))
                kwh_per_unit = float(row["kwh_per_good_unit"]) if pd.notnull(row["kwh_per_good_unit"]) else None
                records.append(
                    Production(
                        machine_id=code_to_id[m_code],
                        production_date=p_date,
                        shift="Shift B",
                        units_produced=units_produced,
                        good_units=good_units,
                        rejected_units=max(0, units_produced - good_units),
                        downtime_minutes=0,
                        kwh_per_good_unit=kwh_per_unit,
                    )
                )
        session.add_all(records)
        await session.commit()
        logger.info(f"Seeded {len(records)} production efficiency records.")

    # 4. Seed Energy Readings (Populate realistic recent telemetry)
    energy_cnt = (await session.execute(select(EnergyReading))).scalars().first()
    if not energy_cnt:
        logger.info("Seeding granular energy telemetry readings...")
        now = datetime.now(timezone.utc)
        energy_records = []
        
        # Load hourly pattern averages by machine to synthesize high-fidelity readings
        hourly_pattern_path = DATASETS_DIR / "hourly_pattern_by_machine.csv"
        if hourly_pattern_path.exists():
            df_hourly = pd.read_csv(hourly_pattern_path)
            for m_code, m_id in code_to_id.items():
                m_rows = df_hourly[df_hourly["machine_id"] == m_code]
                if m_rows.empty:
                    continue
                # Seed past 7 days hourly readings
                for day_offset in range(7):
                    day_ts = now - timedelta(days=day_offset)
                    for _, h_row in m_rows.iterrows():
                        hour = int(h_row["hour"])
                        ts = day_ts.replace(hour=hour, minute=0, second=0, microsecond=0)
                        power_kw = float(h_row["mean_power_kw"])
                        energy_kwh = float(h_row["energy_kwh"]) / 90.0  # Normalized interval kWh
                        
                        energy_records.append(
                            EnergyReading(
                                machine_id=m_id,
                                timestamp=ts,
                                active_power_kw=round(power_kw, 2),
                                energy_kwh=round(energy_kwh, 3),
                                voltage_l1=230.5,
                                voltage_l2=229.8,
                                voltage_l3=230.1,
                                current_l1=round(power_kw * 1.45, 1),
                                current_l2=round(power_kw * 1.43, 1),
                                current_l3=round(power_kw * 1.44, 1),
                                power_factor=0.92,
                                temperature_c=48.0 if "FURN" not in m_code else 842.0,
                                data_quality="valid",
                                anomaly_label=0,
                            )
                        )
            session.add_all(energy_records)
            await session.commit()
            logger.info(f"Seeded {len(energy_records)} historical energy telemetry records.")

    # 5. Seed Carbon Emissions
    carbon_cnt = (await session.execute(select(CarbonEmission))).scalars().first()
    if not carbon_cnt:
        logger.info("Seeding carbon accounting records...")
        today = date.today()
        carbon_records = [
            CarbonEmission(
                date=today - timedelta(days=i),
                scope="Scope 2",
                emission_source="Grid Electricity (MSEDCL 33kV)",
                tons_co2e=round(11.2 - (i * 0.1), 2),
                activity_data=f"{13650 - (i * 120):,} kWh",
                activity_unit="kWh",
                emission_factor=0.82,
                department="Plant-Wide Total",
            )
            for i in range(30)
        ]
        session.add_all(carbon_records)
        await session.commit()
        logger.info(f"Seeded {len(carbon_records)} carbon emissions records.")

    # 6. Seed Compliance Reports
    report_cnt = (await session.execute(select(Report))).scalars().first()
    if not report_cnt:
        reports = [
            Report(
                id="rep-oct-audit",
                title="Monthly Industrial Energy Efficiency & Audit Report",
                category="energy",
                period="October 2026",
                file_size_bytes=2458000,
                file_path="/reports/monthly_energy_audit_oct_2026.pdf",
                author="Vikram Patel",
                status="ready",
            ),
            Report(
                id="rep-carbon-q3",
                title="Q3 FY2026 GHG Scope 1 & Scope 2 Emissions Audit",
                category="carbon",
                period="Q3 FY2026",
                file_size_bytes=3890000,
                file_path="/reports/q3_ghg_emissions_report.pdf",
                author="Compliance Auditor",
                status="ready",
            ),
        ]
        session.add_all(reports)
        await session.commit()

    # 7. Seed Multi-Horizon Forecast Projections
    from app.models.forecast import Forecast
    forecast_cnt = (await session.execute(select(Forecast))).scalars().first()
    if not forecast_cnt:
        logger.info("Seeding multi-horizon forecast table...")
        now = datetime.now(timezone.utc)
        forecast_rows = []
        for h in range(1, 25):
            ts = now + timedelta(hours=h)
            base_kw = 158.0 + (15.0 if 9 <= ts.hour <= 18 else -20.0)
            forecast_rows.append(
                Forecast(
                    machine_id="comp-01",
                    target_timestamp=ts,
                    horizon="24h",
                    forecast_power_kw=round(base_kw, 2),
                    lower_bound_80=round(base_kw * 0.92, 2),
                    upper_bound_80=round(base_kw * 1.08, 2),
                    lower_bound_95=round(base_kw * 0.85, 2),
                    upper_bound_95=round(base_kw * 1.15, 2),
                    model_version="1.2.0-prod",
                    confidence_score=0.94,
                )
            )
        session.add_all(forecast_rows)
        await session.commit()
        logger.info(f"Seeded {len(forecast_rows)} forecast projection records.")

    logger.info("Database seeding successfully verified.")
