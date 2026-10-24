"""
GreenPulse AI - Enterprise User Model
Represents Plant Heads, Energy Managers, Maintenance Managers, and Operators.
Supports Role-Based Access Control (RBAC) and Assigned Machines mapping.
"""
from datetime import datetime
from typing import List, Optional, Set
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin
from app.models.auth import user_roles, user_machines


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False, default="")
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="OPERATOR", nullable=False)
    department: Mapped[str] = mapped_column(String(100), default="Operations", nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)  # active, suspended, pending
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    roles = relationship("Role", secondary=user_roles, back_populates="users", lazy="selectin")
    assigned_machines = relationship("Machine", secondary=user_machines, lazy="selectin")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user")
    simulations = relationship("SimulationHistory", back_populates="user", cascade="all, delete-orphan")

    @property
    def permissions_set(self) -> Set[str]:
        """Collects unique permission codes across all assigned roles."""
        perms = set()
        for r in self.roles:
            for p in getattr(r, "permissions", []):
                perms.add(p.code)
        # Super-admin / Plant Head fallback grant
        if self.role in ["PLANT_HEAD", "admin"] or self.is_admin:
            perms.update([
                "VIEW_DASHBOARD", "VIEW_PLANT", "VIEW_MACHINE", "VIEW_ASSIGNED_MACHINE",
                "VIEW_DIGITAL_TWIN", "VIEW_ENERGY", "VIEW_CARBON", "VIEW_FORECAST",
                "VIEW_ALERTS", "VIEW_RECOMMENDATIONS", "VIEW_SIMULATOR", "VIEW_REPORTS",
                "MANAGE_USERS", "CONFIGURE_THRESHOLDS", "ACKNOWLEDGE_ALERT",
                "UPDATE_MACHINE_STATUS", "SCHEDULE_MAINTENANCE", "APPROVE_MAINTENANCE",
                "EXPORT_REPORTS", "VIEW_AUDIT_LOGS", "APPROVE_RECOMMENDATIONS", "RUN_SIMULATION",
            ])
        return perms

    @property
    def permissions_list(self) -> List[str]:
        return sorted(list(self.permissions_set))

    @property
    def assigned_machine_ids(self) -> List[str]:
        """List of assigned machine IDs (e.g. ['comp-01', 'cnc-01'])."""
        return [m.id for m in self.assigned_machines]

    @property
    def assigned_machine_codes(self) -> List[str]:
        """List of assigned machine codes (e.g. ['COMP-01', 'CNC-01'])."""
        return [m.code for m in self.assigned_machines]

    def has_permission(self, permission_code: str) -> bool:
        """Verifies if the user has a specific permission."""
        if self.is_admin or self.role in ["PLANT_HEAD", "admin"]:
            return True
        return permission_code in self.permissions_set

    def can_access_machine(self, machine_id_or_code: str) -> bool:
        """
        Determines if the user is authorized to inspect/control a machine asset.
        Plant Head & Maintenance Manager can access all machines.
        Operator is restricted strictly to assigned machines.
        """
        if self.is_admin or self.role in ["PLANT_HEAD", "MAINTENANCE_MANAGER", "admin"]:
            return True
        if self.role == "OPERATOR":
            target = machine_id_or_code.lower()
            assigned_ids = [m.id.lower() for m in self.assigned_machines]
            assigned_codes = [m.code.lower() for m in self.assigned_machines]
            return (target in assigned_ids) or (target in assigned_codes)
        # Energy Manager has plant-level aggregated view
        return True
