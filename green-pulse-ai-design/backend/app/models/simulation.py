"""
GreenPulse AI - Simulation History Model
Maintains audit history of what-if parameter evaluations and counterfactual scenarios.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class SimulationHistory(Base, TimestampMixin):
    __tablename__ = "simulation_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    scenario_name: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Input Levers
    production_load_pct: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    runtime_hours: Mapped[float] = mapped_column(Float, default=16.0, nullable=False)
    shift_schedule: Mapped[str] = mapped_column(String(50), default="2-shift", nullable=False)
    base_tariff: Mapped[float] = mapped_column(Float, default=7.20, nullable=False)
    renewable_pct: Mapped[float] = mapped_column(Float, default=22.0, nullable=False)
    
    # Simulated Outputs
    baseline_energy_kwh: Mapped[float] = mapped_column(Float, nullable=False)
    simulated_energy_kwh: Mapped[float] = mapped_column(Float, nullable=False)
    baseline_cost: Mapped[float] = mapped_column(Float, nullable=False)
    simulated_cost: Mapped[float] = mapped_column(Float, nullable=False)
    baseline_carbon_tons: Mapped[float] = mapped_column(Float, nullable=False)
    simulated_carbon_tons: Mapped[float] = mapped_column(Float, nullable=False)
    monthly_net_savings_currency: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Relationships
    user = relationship("User", back_populates="simulations")

    __table_args__ = (
        Index("idx_simulation_created", "created_at"),
    )
