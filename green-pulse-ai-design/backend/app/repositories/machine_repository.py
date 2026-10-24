"""
GreenPulse AI - Machine Repository
Queries equipment definitions, live electrical telemetry, and maintenance records.
"""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.machine import Machine
from app.models.energy import EnergyReading
from app.models.maintenance import MaintenanceHistory
from app.repositories.base import BaseRepository


class MachineRepository(BaseRepository[Machine]):
    def __init__(self, session: AsyncSession):
        super().__init__(Machine, session)

    async def get_by_code(self, code: str) -> Optional[Machine]:
        stmt = select(Machine).where(Machine.code == code)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_with_relations(self, machine_id: str) -> Optional[Machine]:
        stmt = (
            select(Machine)
            .where(Machine.id == machine_id)
            .options(
                selectinload(Machine.maintenance_records),
                selectinload(Machine.anomalies),
                selectinload(Machine.recommendations),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_active_machines(self) -> List[Machine]:
        stmt = select(Machine).where(Machine.is_active == True).order_by(Machine.code)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_latest_reading(self, machine_id: str) -> Optional[EnergyReading]:
        stmt = (
            select(EnergyReading)
            .where(EnergyReading.machine_id == machine_id)
            .order_by(EnergyReading.timestamp.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_recent_readings(self, machine_id: str, limit: int = 24) -> List[EnergyReading]:
        stmt = (
            select(EnergyReading)
            .where(EnergyReading.machine_id == machine_id)
            .order_by(EnergyReading.timestamp.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(reversed(result.scalars().all()))
