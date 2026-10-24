"""
GreenPulse AI - Enterprise Authentication & RBAC Models
Defines Roles, Permissions, UserRoles, RolePermissions, AssignedMachines (UserMachines),
RefreshTokens, and AuditLogs for Enterprise Industrial Security.
"""
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin

# ---------------------------------------------------------------------------
# Association Tables
# ---------------------------------------------------------------------------

user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)

role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
)

user_machines = Table(
    "user_machines",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("machine_id", String(50), ForeignKey("machines.id", ondelete="CASCADE"), primary_key=True),
)


# ---------------------------------------------------------------------------
# Role Model
# ---------------------------------------------------------------------------

class Role(Base, TimestampMixin):
    """
    Enterprise Roles:
    - PLANT_HEAD ("Plant Head")
    - ENERGY_MANAGER ("Energy Manager")
    - MAINTENANCE_MANAGER ("Maintenance Manager")
    - OPERATOR ("Operator")
    """
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    permissions: Mapped[List["Permission"]] = relationship(
        "Permission",
        secondary=role_permissions,
        back_populates="roles",
        lazy="selectin",
    )
    users: Mapped[List["User"]] = relationship(
        "User",
        secondary=user_roles,
        back_populates="roles",
    )


# ---------------------------------------------------------------------------
# Permission Model
# ---------------------------------------------------------------------------

class Permission(Base, TimestampMixin):
    """
    Granular enterprise permissions:
    VIEW_DASHBOARD, VIEW_PLANT, VIEW_MACHINE, VIEW_ASSIGNED_MACHINE,
    VIEW_DIGITAL_TWIN, VIEW_ENERGY, VIEW_CARBON, VIEW_FORECAST,
    VIEW_ALERTS, VIEW_RECOMMENDATIONS, VIEW_SIMULATOR, VIEW_REPORTS,
    MANAGE_USERS, CONFIGURE_THRESHOLDS, ACKNOWLEDGE_ALERT,
    UPDATE_MACHINE_STATUS, SCHEDULE_MAINTENANCE, APPROVE_MAINTENANCE,
    EXPORT_REPORTS, VIEW_AUDIT_LOGS, APPROVE_RECOMMENDATIONS, RUN_SIMULATION.
    """
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    module: Mapped[str] = mapped_column(String(50), default="core", nullable=False)

    # Relationships
    roles: Mapped[List[Role]] = relationship(
        Role,
        secondary=role_permissions,
        back_populates="permissions",
    )


# ---------------------------------------------------------------------------
# Refresh Token Model
# ---------------------------------------------------------------------------

class RefreshToken(Base):
    """
    Stores cryptographic hashes of active refresh tokens for session rotation and revocation.
    """
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    token_hash: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user = relationship("User", back_populates="refresh_tokens")


# ---------------------------------------------------------------------------
# Audit Log Model
# ---------------------------------------------------------------------------

class AuditLog(Base):
    """
    Enterprise Compliance Audit Trail:
    Tracks login, logout, failed login, role changes, user creations,
    permission checks, threshold modifications, and sensitive actions.
    """
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    role: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    action: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="SUCCESS", nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    user = relationship("User", back_populates="audit_logs")
