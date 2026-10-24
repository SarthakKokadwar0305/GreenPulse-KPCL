"""
GreenPulse AI - Settings Service
Coordinates retrieval and persistence of plant operational parameters.
"""
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.settings_repository import SettingsRepository
from app.schemas.settings import (
    SystemSettingsResponse,
    PlantSettingsSchema,
    NotificationSettingsSchema,
    ApiGatewaySettingsSchema,
    UpdateSystemSettingsRequest,
)


class SettingsService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = SettingsRepository(session)

    async def get_settings(self) -> SystemSettingsResponse:
        plant_dict = await self.repo.get_setting("plant")
        notif_dict = await self.repo.get_setting("notifications")
        api_dict = await self.repo.get_setting("api")

        plant = PlantSettingsSchema(**plant_dict) if plant_dict else PlantSettingsSchema()
        notifications = NotificationSettingsSchema(**notif_dict) if notif_dict else NotificationSettingsSchema()
        api = ApiGatewaySettingsSchema(**api_dict) if api_dict else ApiGatewaySettingsSchema()

        return SystemSettingsResponse(
            plant=plant,
            notifications=notifications,
            api=api,
            last_updated=datetime.now(timezone.utc).isoformat(),
        )

    async def update_settings(self, request: UpdateSystemSettingsRequest, user_name: str = "plant_head") -> SystemSettingsResponse:
        if request.plant:
            await self.repo.save_setting("plant", request.plant.model_dump(), updated_by=user_name)
        if request.notifications:
            await self.repo.save_setting("notifications", request.notifications.model_dump(), updated_by=user_name)
        if request.api:
            await self.repo.save_setting("api", request.api.model_dump(), updated_by=user_name)

        return await self.get_settings()
