"""
GreenPulse AI - Energy API Route
Provides multi-resolution energy telemetry: hourly, daily, weekly, monthly, heatmaps, and peak demand.
Clean Architecture: Delegates all domain logic to EnergyService.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_permissions
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.energy import EnergyAnalyticsResponse
from app.services.energy_service import EnergyService

router = APIRouter(prefix="/energy", tags=["Energy"])


@router.get(
    "",
    response_model=ApiResponse[EnergyAnalyticsResponse],
    summary="Get Plant Energy Analytics & Load Profiles",
    include_in_schema=False,
)
@router.get(
    "/analytics",
    response_model=ApiResponse[EnergyAnalyticsResponse],
    summary="Get Plant Energy Analytics & Load Profiles",
    description="Returns hourly, daily, weekly, monthly load profiles, machine comparison, department breakdown, peak demand, and 7x24 heatmap."
)
async def get_energy_analytics(
    time_range: str = Query("24h", description="Time window for analysis (e.g. 24h, 7d, 30d, 12m)"),
    current_user: User = Depends(require_permissions("VIEW_ENERGY")),
    db: AsyncSession = Depends(get_db)
) -> ApiResponse[EnergyAnalyticsResponse]:
    service = EnergyService(db)
    data = await service.get_energy_analytics(time_range=time_range)
    return ApiResponse.ok(data=data, message="Energy analytics fetched successfully")
