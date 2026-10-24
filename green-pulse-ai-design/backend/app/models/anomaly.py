"""
GreenPulse AI - Anomaly Model
Tracks automated fault detection and diagnostics (FDD), root causes, and cost impact.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class Anomaly(Base, TimestampMixin):
    __tablename__ = "anomalies"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)  # e.g., 'anom-01'
    machine_id: Mapped[str] = mapped_column(String(50), ForeignKey("machines.id", ondelete="CASCADE"), index=True, nullable=False)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    
    severity: Mapped[str] = mapped_column(String(30), default="warning", nullable=False)  # critical, warning, info
    status: Mapped[str] = mapped_column(String(30), default="open", nullable=False)  # open, investigating, acknowledged, resolved
    root_cause: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=90.0, nullable=False)
    suggested_action: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Financial metrics
    cost_impact_per_hour: Mapped[float] = mapped_column(Float, default=50.0, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    
    # Resolution metadata
    assigned_engineer: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    work_order_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    machine = relationship("Machine", back_populates="anomalies")

    __table_args__ = (
        Index("idx_anomaly_severity_status", "severity", "status"),
    )
