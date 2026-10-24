"""
GreenPulse AI - Energy Reading Model
Captures high-frequency electrical telemetry, multi-phase voltages, currents, and data quality tags.
"""
from datetime import datetime
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class EnergyReading(Base):
    __tablename__ = "energy_readings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    machine_id: Mapped[str] = mapped_column(String(50), ForeignKey("machines.id", ondelete="CASCADE"), index=True, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    
    # Core Energy Telemetry
    active_power_kw: Mapped[float] = mapped_column(Float, nullable=False)
    energy_kwh: Mapped[float] = mapped_column(Float, nullable=False)
    
    # 3-Phase Electrical Diagnostics
    voltage_l1: Mapped[float] = mapped_column(Float, default=230.0, nullable=False)
    voltage_l2: Mapped[float] = mapped_column(Float, default=230.0, nullable=False)
    voltage_l3: Mapped[float] = mapped_column(Float, default=230.0, nullable=False)
    current_l1: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    current_l2: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    current_l3: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    power_factor: Mapped[float] = mapped_column(Float, default=0.92, nullable=False)
    
    # Thermal & Condition
    temperature_c: Mapped[float] = mapped_column(Float, default=45.0, nullable=False)
    data_quality: Mapped[str] = mapped_column(String(30), default="valid", nullable=False)  # valid, missing, sensor_stuck, invalid_negative
    anomaly_label: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    machine = relationship("Machine", back_populates="readings")

    __table_args__ = (
        Index("idx_machine_timestamp", "machine_id", "timestamp"),
    )
