"""
GreenPulse AI - Base Repository
Generic asynchronous CRUD operations adhering to repository design patterns.
"""
from typing import Any, Generic, List, Optional, Type, TypeVar
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Generic base repository managing entity lifecycle in SQLAlchemy."""

    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get(self, id: Any) -> Optional[ModelType]:
        return await self.session.get(self.model, id)

    async def get_by_id(self, id: Any) -> Optional[ModelType]:
        return await self.get(id)

    async def list_all(self, limit: int = 100, offset: int = 0) -> List[ModelType]:
        stmt = select(self.model).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, entity: ModelType) -> ModelType:
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def delete(self, id: Any) -> bool:
        entity = await self.get(id)
        if entity:
            await self.session.delete(entity)
            await self.session.commit()
            return True
        return False
