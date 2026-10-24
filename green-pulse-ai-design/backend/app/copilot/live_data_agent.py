"""
GreenPulse AI Copilot - Live Backend Data Agent
Directly interfaces with internal application services to fetch live operational telemetry,
machine health indexes, energy analytics, forecasts, anomalies, and active recommendations.
Enforces strict Role-Based Access Control (RBAC) filtering.
"""
import logging
from typing import Dict, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.services.dashboard_service import DashboardService
from app.services.machine_service import MachineService
from app.services.energy_service import EnergyService
from app.services.carbon_service import CarbonService
from app.services.forecast_service import ForecastService
from app.services.anomaly_service import AnomalyService
from app.services.recommendation_service import RecommendationService
from app.services.plant_service import PlantService

logger = logging.getLogger("greenpulse.copilot.live_data")


class LiveDataAgent:
    """Fetches real-time industrial data from GreenPulse backend services with RBAC."""

    def __init__(self, db: AsyncSession, user: User):
        self.db = db
        self.user = user
        self.role = user.role

    async def get_dashboard_summary(self) -> Dict[str, Any]:
        """Fetches plant dashboard KPIs with role-aware masking."""
        service = DashboardService(self.db)
        data = await service.get_dashboard_overview()
        res = data.model_dump() if hasattr(data, "model_dump") else data

        # RBAC Masking for Operators
        if self.role == "OPERATOR":
            if "financial" in res:
                res["financial"] = {
                    "note": "[Financial metrics restricted to Plant Head and Energy Manager]"
                }
            if "plant_kpis" in res and "energy_cost_today_inr" in res["plant_kpis"]:
                res["plant_kpis"]["energy_cost_today_inr"] = "[Restricted]"

        return res

    async def get_highest_energy_machine(self) -> Dict[str, Any]:
        """Finds the single machine drawing the highest power right now."""
        service = MachineService(self.db)
        machines = await service.get_machines()

        if self.role == "OPERATOR":
            # Filter strictly to assigned machines
            assigned = {m.lower() for m in self.user.assigned_machine_ids}
            machines = [
                m for m in machines
                if m.id.lower() in assigned or (getattr(m, "code", "") or getattr(m, "machine_code", "")).lower() in assigned
            ]

        if not machines:
            return {"message": "No machines found or accessible under current role permissions."}

        # Sort by current active power kW descending
        sorted_machines = sorted(machines, key=lambda m: getattr(m, "power_kw", 0.0), reverse=True)
        top = sorted_machines[0]
        m_code = getattr(top, "code", "") or getattr(top, "machine_code", "")
        h_score = getattr(top, "health_score", 0) or getattr(top, "health_index", 0)

        return {
            "machine_id": top.id,
            "machine_name": top.name,
            "machine_code": m_code,
            "power_kw": top.power_kw,
            "energy_today_kwh": getattr(top, "energy_today_kwh", 0.0),
            "status": top.status,
            "health_score": h_score,
            "temperature_c": getattr(top, "temperature_c", 0.0),
            "zone": top.zone,
        }

    async def get_machine_telemetry(self, machine_id_or_code: str) -> Dict[str, Any]:
        """Fetches live SCADA telemetry and health diagnostics for a specific asset."""
        service = MachineService(self.db)
        machine = await service.get_machine_by_id(machine_id_or_code)

        if not machine:
            return {"error": f"Machine asset '{machine_id_or_code}' was not found in factory registry."}

        # Check operator assignment
        if self.role == "OPERATOR":
            assigned_ids = {m.lower() for m in self.user.assigned_machine_ids}
            machine_code_val = (getattr(machine, "code", "") or getattr(machine, "machine_code", "")).upper()
            if machine.id.lower() not in assigned_ids and machine_code_val not in assigned_codes:
                return {
                    "error": f"Access Denied: Machine '{machine.name}' is outside your authorized workstation bay.",
                    "authorized_machines": list(assigned_codes)
                }

        return machine.model_dump() if hasattr(machine, "model_dump") else machine

    async def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Returns active anomaly alerts and threshold exceedance events."""
        service = AnomalyService(self.db)
        anomalies_data = await service.get_anomalies()
        res = anomalies_data.model_dump() if hasattr(anomalies_data, "model_dump") else anomalies_data

        incidents = res.get("active_incidents", []) if isinstance(res, dict) else []

        if self.role == "OPERATOR":
            assigned = {m.lower() for m in self.user.assigned_machine_ids}
            incidents = [
                inc for inc in incidents
                if inc.get("machine_id", "").lower() in assigned or inc.get("machine_code", "").lower() in assigned
            ]

        return incidents[:5]

    async def get_today_forecast(self, horizon: int = 24) -> Dict[str, Any]:
        """Fetches XGBoost energy forecast for the upcoming 24 hours."""
        if not self.user.has_permission("VIEW_FORECAST") and self.role == "OPERATOR":
            return {
                "summary": "Plant-wide 24h predictive load curve is restricted to Energy Management and Plant Head.",
                "status": "RESTRICTED"
            }

        service = ForecastService(self.db)
        forecast_data = await service.get_forecast(horizon_hours=horizon)
        return forecast_data.model_dump() if hasattr(forecast_data, "model_dump") else forecast_data

    async def get_top_recommendations(self) -> List[Dict[str, Any]]:
        """Fetches prioritized energy conservation opportunities with estimated savings."""
        service = RecommendationService(self.db)
        recs_data = await service.get_recommendations()
        res = recs_data.model_dump() if hasattr(recs_data, "model_dump") else recs_data

        items = res.get("recommendations", []) if isinstance(res, dict) else []

        # Sort by ROI or monthly savings
        items.sort(key=lambda x: x.get("monthly_savings_inr", 0), reverse=True)

        if self.role == "OPERATOR":
            # Mask financial savings for operator
            sanitized = []
            for item in items:
                copy_item = dict(item)
                copy_item["monthly_savings_inr"] = "[Restricted to Management]"
                copy_item["investment_cost_inr"] = "[Restricted to Management]"
                sanitized.append(copy_item)
            return sanitized[:4]

        return items[:4]

    async def get_carbon_summary(self) -> Dict[str, Any]:
        """Fetches carbon footprint and GHG emission breakdown."""
        if not self.user.has_permission("VIEW_CARBON") and self.role == "OPERATOR":
            return {"status": "RESTRICTED", "message": "Carbon accounting reports require Energy Manager or Plant Head access."}

        service = CarbonService(self.db)
        data = await service.get_carbon_accounting(time_range="month")
        return data.model_dump() if hasattr(data, "model_dump") else data
