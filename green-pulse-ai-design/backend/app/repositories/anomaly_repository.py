"""
GreenPulse AI - Anomaly Repository
Manages equipment incident cards, severity filters, and work order tracking.
"""
from typing import List, Optional
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.anomaly import Anomaly
from app.repositories.base import BaseRepository


class AnomalyRepository(BaseRepository[Anomaly]):
    def __init__(self, session: AsyncSession):
        super().__init__(Anomaly, session)

    async def list_by_filter(
        self,
        severity: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Anomaly]:
        stmt = select(Anomaly).options(selectinload(Anomaly.machine)).order_by(Anomaly.detected_at.desc())
        if severity and severity != "all":
            stmt = stmt.where(Anomaly.severity == severity)
        if status and status != "all":
            stmt = stmt.where(Anomaly.status == status)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_active_count(self) -> int:
        stmt = select(Anomaly).where(Anomaly.status.in_(["open", "investigating"]))
        result = await self.session.execute(stmt)
        return len(result.scalars().all())

    async def update_status(self, anomaly_id: str, new_status: str, engineer: Optional[str] = None) -> Optional[Anomaly]:
        anomaly = await self.get(anomaly_id)
        if anomaly:
            anomaly.status = new_status
            if engineer:
                anomaly.assigned_engineer = engineer
            await self.session.commit()
            await self.session.refresh(anomaly)
        return anomaly
