"""
GreenPulse AI - Carbon Emission Model
Stores GHG Protocol Scope 1 (Direct) and Scope 2 (Indirect) corporate carbon disclosures.
"""
from datetime import date
from typing import Optional
from sqlalchemy import Date, Float, Integer, String, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class CarbonEmission(Base):
    __tablename__ = "carbon_emissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    scope: Mapped[str] = mapped_column(String(20), nullable=False)  # 'Scope 1' or 'Scope 2'
    emission_source: Mapped[str] = mapped_column(String(150), nullable=False)  # e.g., 'Natural Gas Furnace'
    tons_co2e: Mapped[float] = mapped_column(Float, nullable=False)
    activity_data: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., '1,140 Nm3'
    activity_unit: Mapped[str] = mapped_column(String(30), nullable=False)  # e.g., 'Nm3', 'kWh'
    emission_factor: Mapped[float] = mapped_column(Float, nullable=False)
    department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    __table_args__ = (
        Index("idx_carbon_date_scope", "date", "scope"),
    )
