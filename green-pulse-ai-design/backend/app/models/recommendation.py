"""
GreenPulse AI - Recommendation Model
Represents AI-generated prescriptive Energy Conservation Measures (ECMs) with verified ROI.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class Recommendation(Base, TimestampMixin):
    __tablename__ = "recommendations"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)  # e.g., 'rec-01'
    machine_id: Mapped[Optional[str]] = mapped_column(String(50), ForeignKey("machines.id", ondelete="SET NULL"), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # 'Load Shifting', 'Asset Tuning', 'Automation', etc.
    priority: Mapped[str] = mapped_column(String(30), default="Medium", nullable=False)  # High, Medium, Low
    
    # Financial and Abatement Metrics
    estimated_savings_kwh_per_month: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    estimated_savings_currency_per_month: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    carbon_reduction_tons_per_month: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    payback_months: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    roi_percent: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=90.0, nullable=False)
    
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    is_applied: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    applied_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    machine = relationship("Machine", back_populates="recommendations")

    __table_args__ = (
        Index("idx_rec_priority_category", "priority", "category"),
    )
