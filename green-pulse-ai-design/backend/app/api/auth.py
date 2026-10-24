"""
GreenPulse AI - Authentication & RBAC API Endpoints
Provides login, OAuth2 token flow, token rotation, logout, current user profile,
user registration (Plant Head only), and audit trail queries.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_permissions, require_roles
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserCreateRequest,
    UserResponse,
    UserSummary,
    RoleResponse,
    AuditLogResponse,
)
from app.schemas.common import ApiResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication & RBAC"])


def get_client_ip(request: Request) -> Optional[str]:
    """Extracts client IP address supporting reverse proxies."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


@router.post("/login", response_model=ApiResponse[TokenResponse], summary="Enterprise User Login")
async def login(
    credentials: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[TokenResponse]:
    """
    Authenticates plant personnel via Username/Email and password.
    Returns JWT access token with embedded permissions and cryptographically hashed refresh token.
    """
    service = AuthService(db)
    ip_addr = get_client_ip(request)
    user_agent = request.headers.get("User-Agent")
    tokens = await service.authenticate_user(credentials, ip_address=ip_addr, user_agent=user_agent)
    return ApiResponse.ok(data=tokens, message=f"Authentication successful. Welcome, {tokens.user.full_name}.")


@router.post("/token", response_model=TokenResponse, summary="OAuth2 Password Flow Token Endpoint")
async def oauth2_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Standard OAuth2 password flow endpoint powering OpenAPI / Swagger 'Authorize' modal.
    """
    service = AuthService(db)
    ip_addr = get_client_ip(request)
    user_agent = request.headers.get("User-Agent")
    credentials = LoginRequest(username_or_email=form_data.username, password=form_data.password)
    tokens = await service.authenticate_user(credentials, ip_address=ip_addr, user_agent=user_agent)
    return tokens


@router.post("/refresh", response_model=ApiResponse[TokenResponse], summary="Rotate Refresh Token")
async def refresh_token(
    refresh_req: RefreshTokenRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[TokenResponse]:
    """
    Rotates existing refresh token, revoking the old one and issuing a brand new access and refresh token pair.
    """
    service = AuthService(db)
    ip_addr = get_client_ip(request)
    tokens = await service.refresh_access_token(refresh_req, ip_address=ip_addr)
    return ApiResponse.ok(data=tokens, message="Access credentials renewed successfully.")


@router.post("/logout", response_model=ApiResponse[dict], summary="User Logout")
async def logout(
    request: Request,
    refresh_req: Optional[RefreshTokenRequest] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[dict]:
    """
    Terminates current session and invalidates active refresh tokens in the database.
    """
    service = AuthService(db)
    ip_addr = get_client_ip(request)
    token_str = refresh_req.refresh_token if refresh_req else None
    await service.logout_user(current_user, refresh_token_str=token_str, ip_address=ip_addr)
    return ApiResponse.ok(data={"status": "LOGGED_OUT"}, message="Logged out successfully.")


@router.get("/me", response_model=ApiResponse[UserSummary], summary="Current User Profile & Permissions")
async def get_me(
    current_user: User = Depends(get_current_user),
) -> ApiResponse[UserSummary]:
    """
    Returns the profile, enterprise role, granted permissions, and assigned machinery for the authenticated user.
    """
    summary = UserSummary(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        department=current_user.department,
        status=current_user.status,
        is_active=current_user.is_active,
        is_admin=current_user.is_admin,
        assigned_machines=current_user.assigned_machine_ids,
        permissions=current_user.permissions_list,
        last_login=current_user.last_login,
    )
    return ApiResponse.ok(data=summary, message="User profile and permissions retrieved.")


@router.post(
    "/register",
    response_model=ApiResponse[UserResponse],
    summary="Register New User (Plant Head / Admin Only)",
)
async def register_user(
    request: Request,
    user_data: UserCreateRequest,
    current_user: User = Depends(require_permissions("MANAGE_USERS")),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[UserResponse]:
    """
    Creates a new user profile with assigned role, department, and optional machine assignments.
    Restricted to Plant Head / Administrator.
    """
    service = AuthService(db)
    ip_addr = get_client_ip(request)
    new_user = await service.register_user(user_data, creator=current_user, ip_address=ip_addr)
    return ApiResponse.ok(
        data=new_user,
        message=f"User '{new_user.username}' successfully registered with role '{new_user.role}'.",
    )


@router.get(
    "/users",
    response_model=ApiResponse[List[UserResponse]],
    summary="List Plant Personnel (Plant Head Only)",
)
async def list_users(
    current_user: User = Depends(require_permissions("MANAGE_USERS")),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[List[UserResponse]]:
    """
    Lists all registered platform personnel with roles, departments, and assigned machines.
    """
    service = AuthService(db)
    users = await service.get_all_users()
    return ApiResponse.ok(data=users, message=f"Retrieved {len(users)} registered users.")


@router.get(
    "/roles",
    response_model=ApiResponse[List[RoleResponse]],
    summary="List Roles & Permission Mapping",
)
async def list_roles(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[List[RoleResponse]]:
    """
    Returns enterprise role definitions and their granular permission grants.
    """
    service = AuthService(db)
    roles = await service.get_all_roles()
    return ApiResponse.ok(data=roles, message=f"Retrieved {len(roles)} enterprise roles.")


@router.get(
    "/audit-logs",
    response_model=ApiResponse[List[AuditLogResponse]],
    summary="View Security & Compliance Audit Trail (Plant Head Only)",
)
async def get_audit_logs(
    limit: int = 50,
    offset: int = 0,
    action: Optional[str] = None,
    current_user: User = Depends(require_permissions("VIEW_AUDIT_LOGS")),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[List[AuditLogResponse]]:
    """
    Queries immutable audit trail for security compliance, authentication audits, and sensitive operations.
    """
    service = AuthService(db)
    logs = await service.get_audit_logs(limit=limit, offset=offset, action=action)
    return ApiResponse.ok(data=logs, message=f"Retrieved {len(logs)} audit log entries.")
