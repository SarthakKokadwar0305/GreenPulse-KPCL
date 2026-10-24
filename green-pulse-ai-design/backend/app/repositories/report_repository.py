"""
GreenPulse AI - Report Repository
Queries and persists generated compliance documents.
"""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.report import Report
from app.repositories.base import BaseRepository


class ReportRepository(BaseRepository[Report]):
    def __init__(self, session: AsyncSession):
        super().__init__(Report, session)

    async def list_by_category(self, category: Optional[str] = None) -> List[Report]:
        stmt = select(Report).order_by(Report.created_at.desc())
        if category and category != "all":
            stmt = stmt.where(Report.category == category)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
