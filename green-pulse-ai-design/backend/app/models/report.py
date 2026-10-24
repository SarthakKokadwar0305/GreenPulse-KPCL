"""
GreenPulse AI - Report Model
Stores generated enterprise energy audits, GHG filings, and scheduled reporting exports.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, Integer, String, Index, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin


class Report(Base, TimestampMixin):
    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)  # e.g., 'rep-01'
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # 'energy', 'carbon', 'forecast', 'anomaly'
    period: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. 'October 2026'
    file_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    file_size_bytes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="ready", nullable=False)
    author: Mapped[str] = mapped_column(String(100), default="GreenPulse System", nullable=False)
    verification_hash: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    summary_stats: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    __table_args__ = (
        Index("idx_report_category_status", "category", "status"),
    )
