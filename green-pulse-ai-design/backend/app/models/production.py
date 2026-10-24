"""
GreenPulse AI - Production Model
Captures manufacturing shift output, good units, rejects, and specific energy efficiency.
"""
from datetime import date
from typing import Optional
from sqlalchemy import Date, Float, ForeignKey, Integer, String, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Production(Base):
    __tablename__ = "production"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    machine_id: Mapped[str] = mapped_column(String(50), ForeignKey("machines.id", ondelete="CASCADE"), index=True, nullable=False)
    production_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    shift: Mapped[str] = mapped_column(String(20), default="Shift B", nullable=False)
    
    units_produced: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    good_units: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rejected_units: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    downtime_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    kwh_per_good_unit: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Relationships
    machine = relationship("Machine", back_populates="production_records")

    __table_args__ = (
        Index("idx_machine_production_date", "machine_id", "production_date"),
    )
