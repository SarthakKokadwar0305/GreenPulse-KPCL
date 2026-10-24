"""
GreenPulse AI - Authentication & RBAC Schemas
Pydantic contracts for credentials, tokens, users, roles, and audit logging.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    username_or_email: str = Field(..., description="Username or registered email address")
    password: str = Field(..., description="User secret password")


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="Valid JWT refresh token")


class UserSummary(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: str
    department: str
    status: str
    is_active: bool
    is_admin: bool
    assigned_machines: List[str] = Field(default_factory=list, description="IDs of assigned machine assets")
    permissions: List[str] = Field(default_factory=list, description="Explicit granted RBAC permissions")
    last_login: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in_seconds: int
    user: UserSummary


class TokenPayload(BaseModel):
    sub: str
    username: str
    email: str
    role: str
    permissions: List[str] = Field(default_factory=list)
    assigned_machines: List[str] = Field(default_factory=list)
    type: str
    exp: int
    iat: int


class UserCreateRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., min_length=5, max_length=255, description="Corporate email address")
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2, max_length=100)
    role: str = Field(..., description="Role code: PLANT_HEAD, ENERGY_MANAGER, MAINTENANCE_MANAGER, or OPERATOR")
    department: str = Field(default="Operations")
    assigned_machine_ids: Optional[List[str]] = Field(default=None, description="Optional list of machine IDs for Operator role")


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: str
    department: str
    status: str
    is_active: bool
    is_admin: bool
    assigned_machines: List[str] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list)
    last_login: Optional[datetime] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class PermissionResponse(BaseModel):
    id: int
    code: str
    name: str
    description: Optional[str] = None
    module: str

    model_config = ConfigDict(from_attributes=True)


class RoleResponse(BaseModel):
    id: int
    code: str
    name: str
    description: Optional[str] = None
    permissions: List[PermissionResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    username: Optional[str] = None
    role: Optional[str] = None
    action: str
    details: Optional[str] = None
    ip_address: Optional[str] = None
    status: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class MachineAssignmentRequest(BaseModel):
    machine_ids: List[str] = Field(..., description="List of machine IDs to assign to the user")
