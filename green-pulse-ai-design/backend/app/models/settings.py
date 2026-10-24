"""
GreenPulse AI - System Settings Model
Persists plant configurations, SCADA gateway registers, and notification thresholds.
"""
from typing import Optional
from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin


class SystemSetting(Base, TimestampMixin):
    __tablename__ = "system_settings"

    key: Mapped[str] = mapped_column(String(50), primary_key=True)  # e.g. 'plant_config', 'notification_config'
    value: Mapped[dict] = mapped_column(JSON, nullable=False)
    updated_by: Mapped[str] = mapped_column(String(100), default="plant_head", nullable=False)
