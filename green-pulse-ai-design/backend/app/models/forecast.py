"""
GreenPulse AI - Forecast Model
Stores machine learning multi-horizon predictions with statistical confidence intervals.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class Forecast(Base, TimestampMixin):
    __tablename__ = "forecasts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    machine_id: Mapped[Optional[str]] = mapped_column(String(50), ForeignKey("machines.id", ondelete="CASCADE"), nullable=True, index=True)
    target_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    horizon: Mapped[str] = mapped_column(String(30), default="24h", nullable=False)  # 24h, 7d, 30d
    
    forecast_power_kw: Mapped[float] = mapped_column(Float, nullable=False)
    lower_bound_80: Mapped[float] = mapped_column(Float, nullable=False)
    upper_bound_80: Mapped[float] = mapped_column(Float, nullable=False)
    lower_bound_95: Mapped[float] = mapped_column(Float, nullable=False)
    upper_bound_95: Mapped[float] = mapped_column(Float, nullable=False)
    
    model_version: Mapped[str] = mapped_column(String(50), default="TFT-v1.0", nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.95, nullable=False)

    # Relationships
    machine = relationship("Machine", back_populates="forecasts")

    __table_args__ = (
        Index("idx_forecast_target", "target_timestamp", "horizon"),
    )
