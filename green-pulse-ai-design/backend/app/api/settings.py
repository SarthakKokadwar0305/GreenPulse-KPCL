"""
GreenPulse AI - Settings API Route
Provides endpoints for retrieving and persisting facility configurations, SCADA thresholds, and security policies.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_permissions, get_current_user
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.settings import (
    SystemSettingsResponse,
    UpdateSystemSettingsRequest,
)
from app.services.settings_service import SettingsService

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get(
    "",
    response_model=ApiResponse[SystemSettingsResponse],
    summary="Get System Settings & Configuration",
    description="Returns plant parameters, SCADA gateway configuration, and alarm thresholds."
)
async def get_system_settings(
    current_user: User = Depends(require_permissions("VIEW_SETTINGS")),
    db: AsyncSession = Depends(get_db)
) -> ApiResponse[SystemSettingsResponse]:
    service = SettingsService(db)
    data = await service.get_settings()
    return ApiResponse.ok(data=data, message="System settings fetched successfully")


@router.post(
    "",
    response_model=ApiResponse[SystemSettingsResponse],
    summary="Update System Settings & Persist",
    description="Updates plant parameters, contracted limits, or SCADA connection registers."
)
@router.put(
    "",
    response_model=ApiResponse[SystemSettingsResponse],
    include_in_schema=False
)
async def update_system_settings(
    request: UpdateSystemSettingsRequest,
    current_user: User = Depends(require_permissions("EDIT_SETTINGS")),
    db: AsyncSession = Depends(get_db)
) -> ApiResponse[SystemSettingsResponse]:
    service = SettingsService(db)
    updated = await service.update_settings(request, user_name=current_user.username or current_user.email)
    return ApiResponse.ok(data=updated, message="System settings updated and persisted successfully")
