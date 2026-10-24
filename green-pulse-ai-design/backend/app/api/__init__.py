"""
GreenPulse AI - API Package
Aggregates all API route modules into a single unified router.
"""
from fastapi import APIRouter

from app.api.dashboard import router as dashboard_router
from app.api.plant import router as plant_router
from app.api.machines import router as machines_router
from app.api.energy import router as energy_router
from app.api.carbon import router as carbon_router
from app.api.forecast import router as forecast_router
from app.api.anomaly import router as anomaly_router
from app.api.recommendations import router as recommendations_router
from app.api.simulator import router as simulator_router
from app.api.reports import router as reports_router
from app.api.auth import router as auth_router
from app.api.settings import router as settings_router
from app.api.copilot import router as copilot_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(dashboard_router)
api_router.include_router(plant_router)
api_router.include_router(machines_router)
api_router.include_router(energy_router)
api_router.include_router(carbon_router)
api_router.include_router(forecast_router)
api_router.include_router(anomaly_router)
api_router.include_router(recommendations_router)
api_router.include_router(simulator_router)
api_router.include_router(reports_router)
api_router.include_router(settings_router)
api_router.include_router(copilot_router)

__all__ = ["api_router"]

