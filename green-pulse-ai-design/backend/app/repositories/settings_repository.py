"""
GreenPulse AI - Settings Repository
Handles persistence of system settings in the database.
"""
from typing import Optional, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.settings import SystemSetting
from app.repositories.base import BaseRepository


class SettingsRepository(BaseRepository[SystemSetting]):
    def __init__(self, session: AsyncSession):
        super().__init__(SystemSetting, session)

    async def get_setting(self, key: str) -> Optional[Dict[str, Any]]:
        stmt = select(SystemSetting).where(SystemSetting.key == key)
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()
        return record.value if record else None

    async def save_setting(self, key: str, value: Dict[str, Any], updated_by: str = "plant_head") -> SystemSetting:
        stmt = select(SystemSetting).where(SystemSetting.key == key)
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()
        if record:
            record.value = value
            record.updated_by = updated_by
        else:
            record = SystemSetting(key=key, value=value, updated_by=updated_by)
            self.session.add(record)
        await self.session.commit()
        await self.session.refresh(record)
        return record
