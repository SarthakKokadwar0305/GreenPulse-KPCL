"""
GreenPulse AI - Recommendation Repository
Manages Energy Conservation Measures (ECMs) and application status.
"""
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.recommendation import Recommendation
from app.repositories.base import BaseRepository


class RecommendationRepository(BaseRepository[Recommendation]):
    def __init__(self, session: AsyncSession):
        super().__init__(Recommendation, session)

    async def list_by_category(self, category: Optional[str] = None) -> List[Recommendation]:
        stmt = select(Recommendation).options(selectinload(Recommendation.machine)).order_by(Recommendation.priority)
        if category and category != "all":
            stmt = stmt.where(Recommendation.category == category)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def apply_recommendation(self, rec_id: str) -> Optional[Recommendation]:
        rec = await self.get(rec_id)
        if rec:
            rec.is_applied = True
            rec.applied_at = datetime.now(timezone.utc)
            await self.session.commit()
            await self.session.refresh(rec)
        return rec
