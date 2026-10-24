"""
GreenPulse AI - Carbon API Route
Provides GHG Protocol Scope 1 & 2 carbon accounting, emission intensity, and sustainability scores.
Clean Architecture: Delegates all domain logic to CarbonService.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_permissions
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.carbon import CarbonAccountingResponse
from app.services.carbon_service import CarbonService

router = APIRouter(prefix="/carbon", tags=["Carbon"])


@router.get(
    "",
    response_model=ApiResponse[CarbonAccountingResponse],
    summary="Get Carbon Accounting & GHG Protocol Breakdown",
    include_in_schema=False,
)
@router.get(
    "/accounting",
    response_model=ApiResponse[CarbonAccountingResponse],
    summary="Get Carbon Accounting & GHG Protocol Breakdown",
    description="Returns Scope 1 & Scope 2 breakdowns, department and machine emissions, net zero trajectories, and sustainability score."
)
async def get_carbon_accounting(
    time_range: str = Query("month", description="Aggregation timeframe: month, quarter, year"),
    current_user: User = Depends(require_permissions("VIEW_CARBON")),
    db: AsyncSession = Depends(get_db)
) -> ApiResponse[CarbonAccountingResponse]:
    service = CarbonService(db)
    data = await service.get_carbon_accounting(time_range=time_range)
    return ApiResponse.ok(data=data, message="Carbon accounting metrics fetched successfully")
