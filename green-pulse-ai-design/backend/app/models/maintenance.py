"""
GreenPulse AI - Maintenance History Model
Tracks mechanical overhauls, sensor recalibrations, and maintenance down-times.
"""
from datetime import date
from typing import Optional
from sqlalchemy import Date, Float, ForeignKey, Integer, String, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class MaintenanceHistory(Base, TimestampMixin):
    __tablename__ = "maintenance_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    machine_id: Mapped[str] = mapped_column(String(50), ForeignKey("machines.id", ondelete="CASCADE"), index=True, nullable=False)
    service_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    service_type: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., 'Oil & Filter Replacement'
    technician_name: Mapped[str] = mapped_column(String(100), nullable=False)
    notes: Mapped[str] = mapped_column(Text, nullable=False)
    parts_replaced: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    downtime_hours: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)

    # Relationships
    machine = relationship("Machine", back_populates="maintenance_records")

    __table_args__ = (
        Index("idx_maint_machine_date", "machine_id", "service_date"),
    )
