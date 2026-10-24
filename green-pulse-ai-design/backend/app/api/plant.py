"""
GreenPulse AI - Plant API Route
Provides factory-wide digital twin telemetry, department breakdowns, shift data, and timeline events.
Clean Architecture: Delegates all domain logic to PlantService.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_permissions
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.plant import PlantOverviewResponse
from app.services.plant_service import PlantService

router = APIRouter(prefix="/plant", tags=["Plant"])


@router.get(
    "",
    response_model=ApiResponse[PlantOverviewResponse],
    summary="Get Factory Digital Twin Overview",
    include_in_schema=False,
)
@router.get(
    "/overview",
    response_model=ApiResponse[PlantOverviewResponse],
    summary="Get Factory Digital Twin Overview",
    description="Returns production summary, department-level telemetry, shift schedule, utility consumption, and factory timeline."
)
async def get_plant_overview(
    current_user: User = Depends(require_permissions("VIEW_PLANT")),
    db: AsyncSession = Depends(get_db)
) -> ApiResponse[PlantOverviewResponse]:
    service = PlantService(db)
    data = await service.get_plant_overview()
    return ApiResponse.ok(data=data, message="Plant overview telemetry fetched successfully")
