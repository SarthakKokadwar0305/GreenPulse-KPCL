"""
GreenPulse AI - Dashboard API Route
Provides real-time plant KPIs, energy, financial metrics, and operational alerts.
Clean Architecture: Delegates all domain logic to DashboardService.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_permissions
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.dashboard import DashboardOverviewResponse
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "",
    response_model=ApiResponse[DashboardOverviewResponse],
    summary="Get Plant Real-Time Dashboard Overview",
    include_in_schema=False,
)
@router.get(
    "/overview",
    response_model=ApiResponse[DashboardOverviewResponse],
    summary="Get Plant Real-Time Dashboard Overview",
    description="Returns high-level plant KPIs, active machines, demand, costs, carbon footprint, and priority alerts."
)
async def get_dashboard_overview(
    current_user: User = Depends(require_permissions("VIEW_DASHBOARD")),
    db: AsyncSession = Depends(get_db)
) -> ApiResponse[DashboardOverviewResponse]:
    service = DashboardService(db)
    data = await service.get_dashboard_overview()
    return ApiResponse.ok(data=data, message="Dashboard overview fetched successfully")
