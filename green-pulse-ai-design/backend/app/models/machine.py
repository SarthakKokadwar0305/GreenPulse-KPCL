"""
GreenPulse AI - Machine Model
Represents industrial factory assets (Air Compressor, CNC, Heat Furnace, Paint Booth, Cooling Pump, Assembly Line).
"""
from typing import List, Optional
from sqlalchemy import Boolean, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class Machine(Base, TimestampMixin):
    __tablename__ = "machines"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)  # e.g., 'air-compressor', 'cnc-machine'
    code: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)  # e.g. 'COMP-01'
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    short_name: Mapped[str] = mapped_column(String(50), nullable=False)
    process_type: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. 'Air compressor'
    zone: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. 'Utilities Block A'
    icon_key: Mapped[str] = mapped_column(String(50), default="cpu", nullable=False)
    rated_power_kw: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="running", nullable=False)  # running, idle, warning, fault
    health_score: Mapped[int] = mapped_column(Integer, default=90, nullable=False)
    model_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    serial_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    readings = relationship("EnergyReading", back_populates="machine", cascade="all, delete-orphan")
    production_records = relationship("Production", back_populates="machine", cascade="all, delete-orphan")
    maintenance_records = relationship("MaintenanceHistory", back_populates="machine", cascade="all, delete-orphan")
    anomalies = relationship("Anomaly", back_populates="machine", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="machine", cascade="all, delete-orphan")
    forecasts = relationship("Forecast", back_populates="machine", cascade="all, delete-orphan")
