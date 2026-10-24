"""
GreenPulse AI - Authentication & RBAC Domain Service
Encapsulates credential verification, JWT issuance, token rotation,
role management, user creation, and enterprise compliance audit logging.
"""
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.logging import logger
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_token,
)
from app.models.user import User
from app.models.auth import Role, Permission, RefreshToken, AuditLog
from app.models.machine import Machine
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


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def log_audit(
        self,
        action: str,
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        role: Optional[str] = None,
        details: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        status_val: str = "SUCCESS",
    ) -> AuditLog:
        """Records an immutable security audit trail event."""
        log_entry = AuditLog(
            user_id=user_id,
            username=username,
            role=role,
            action=action,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            status=status_val,
            timestamp=datetime.now(timezone.utc),
        )
        self.db.add(log_entry)
        await self.db.commit()
        return log_entry

    async def authenticate_user(
        self,
        request: LoginRequest,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> TokenResponse:
        """Verifies credentials, issues tokens, rotates sessions, and logs audit."""
        login_id = request.username_or_email.strip().lower()

        stmt = (
            select(User)
            .options(
                selectinload(User.roles).selectinload(Role.permissions),
                selectinload(User.assigned_machines),
            )
            .where(
                (User.email.ilike(login_id)) | (User.username.ilike(login_id))
            )
        )
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user or not verify_password(request.password, user.hashed_password):
            await self.log_audit(
                action="LOGIN_FAILED",
                username=login_id,
                details=f"Invalid credentials attempt for identifier '{login_id}'",
                ip_address=ip_address,
                user_agent=user_agent,
                status_val="FAILURE",
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username/email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active or user.status == "suspended":
            await self.log_audit(
                action="LOGIN_BLOCKED_INACTIVE",
                user_id=user.id,
                username=user.username,
                role=user.role,
                details="Attempted login on deactivated/suspended account",
                ip_address=ip_address,
                user_agent=user_agent,
                status_val="BLOCKED",
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive or suspended. Contact plant administrator.",
            )

        # Update last login timestamp
        user.last_login = datetime.now(timezone.utc)

        # Issue Access Token
        access_token_data = {
            "sub": str(user.id),
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "permissions": user.permissions_list,
            "assigned_machines": user.assigned_machine_ids,
        }
        access_token = create_access_token(access_token_data)

        # Issue Refresh Token and store hash in database
        refresh_token = create_refresh_token({"sub": str(user.id)})
        refresh_expires = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        token_entry = RefreshToken(
            user_id=user.id,
            token_hash=hash_token(refresh_token),
            expires_at=refresh_expires,
            revoked=False,
        )
        self.db.add(token_entry)
        await self.db.commit()

        # Log Successful Login
        await self.log_audit(
            action="LOGIN_SUCCESS",
            user_id=user.id,
            username=user.username,
            role=user.role,
            details=f"Session established. Role: {user.role}, Assigned machines: {len(user.assigned_machines)}",
            ip_address=ip_address,
            user_agent=user_agent,
            status_val="SUCCESS",
        )

        user_summary = UserSummary(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            department=user.department,
            status=user.status,
            is_active=user.is_active,
            is_admin=user.is_admin,
            assigned_machines=user.assigned_machine_ids,
            permissions=user.permissions_list,
            last_login=user.last_login,
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_summary,
        )

    async def refresh_access_token(
        self,
        request: RefreshTokenRequest,
        ip_address: Optional[str] = None,
    ) -> TokenResponse:
        """Rotates refresh tokens and issues fresh access tokens."""
        try:
            payload = decode_token(request.refresh_token)
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type: Expected refresh token.",
                )
            user_id = int(payload.get("sub"))
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid refresh token: {str(e)}",
            )

        token_h = hash_token(request.refresh_token)
        now = datetime.now(timezone.utc)
        stmt = select(RefreshToken).where(
            RefreshToken.token_hash == token_h,
            RefreshToken.revoked == False,
            RefreshToken.expires_at > now,
        )
        result = await self.db.execute(stmt)
        token_record = result.scalar_one_or_none()

        if not token_record:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has been revoked, expired, or is invalid.",
            )

        # Revoke old refresh token (Token Rotation!)
        token_record.revoked = True

        # Fetch user
        user_stmt = (
            select(User)
            .options(
                selectinload(User.roles).selectinload(Role.permissions),
                selectinload(User.assigned_machines),
            )
            .where(User.id == user_id)
        )
        user_res = await self.db.execute(user_stmt)
        user = user_res.scalar_one_or_none()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account inactive or deleted.",
            )

        # Issue new tokens
        access_token_data = {
            "sub": str(user.id),
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "permissions": user.permissions_list,
            "assigned_machines": user.assigned_machine_ids,
        }
        new_access_token = create_access_token(access_token_data)
        new_refresh_token = create_refresh_token({"sub": str(user.id)})
        new_expires = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        new_token_record = RefreshToken(
            user_id=user.id,
            token_hash=hash_token(new_refresh_token),
            expires_at=new_expires,
            revoked=False,
        )
        self.db.add(new_token_record)
        await self.db.commit()

        await self.log_audit(
            action="TOKEN_ROTATED",
            user_id=user.id,
            username=user.username,
            role=user.role,
            details="Rotated refresh token and renewed access credentials",
            ip_address=ip_address,
        )

        user_summary = UserSummary(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            department=user.department,
            status=user.status,
            is_active=user.is_active,
            is_admin=user.is_admin,
            assigned_machines=user.assigned_machine_ids,
            permissions=user.permissions_list,
            last_login=user.last_login,
        )

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_summary,
        )

    async def logout_user(
        self,
        user: User,
        refresh_token_str: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> bool:
        """Revokes refresh tokens on logout and logs audit."""
        if refresh_token_str:
            token_h = hash_token(refresh_token_str)
            stmt = select(RefreshToken).where(RefreshToken.token_hash == token_h)
            result = await self.db.execute(stmt)
            record = result.scalar_one_or_none()
            if record:
                record.revoked = True
        else:
            # Revoke all active refresh tokens for the user
            stmt = select(RefreshToken).where(RefreshToken.user_id == user.id, RefreshToken.revoked == False)
            result = await self.db.execute(stmt)
            for record in result.scalars().all():
                record.revoked = True

        await self.db.commit()
        await self.log_audit(
            action="LOGOUT",
            user_id=user.id,
            username=user.username,
            role=user.role,
            details="User logged out; active refresh tokens invalidated.",
            ip_address=ip_address,
        )
        return True

    async def register_user(
        self,
        request: UserCreateRequest,
        creator: User,
        ip_address: Optional[str] = None,
    ) -> UserResponse:
        """Registers a new user (Plant Head / Admin only)."""
        # Validate unique username and email
        existing_stmt = select(User).where(
            (User.email.ilike(request.email)) | (User.username.ilike(request.username))
        )
        existing = (await self.db.execute(existing_stmt)).scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this username or email already exists.",
            )

        # Validate Role
        role_code = request.role.upper().replace(" ", "_")
        role_stmt = select(Role).options(selectinload(Role.permissions)).where(Role.code == role_code)
        role = (await self.db.execute(role_stmt)).scalar_one_or_none()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role code '{request.role}'. Valid roles: PLANT_HEAD, ENERGY_MANAGER, MAINTENANCE_MANAGER, OPERATOR",
            )

        new_user = User(
            username=request.username.strip(),
            email=request.email.strip().lower(),
            hashed_password=hash_password(request.password),
            full_name=request.full_name.strip(),
            role=role.code,
            department=request.department,
            status="active",
            is_active=True,
            is_admin=(role.code == "PLANT_HEAD"),
        )
        new_user.roles.append(role)

        # Assign machines if provided (for Operators)
        if request.assigned_machine_ids:
            machine_stmt = select(Machine).where(Machine.id.in_(request.assigned_machine_ids))
            machines = (await self.db.execute(machine_stmt)).scalars().all()
            new_user.assigned_machines.extend(machines)

        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)

        await self.log_audit(
            action="USER_CREATED",
            user_id=creator.id,
            username=creator.username,
            role=creator.role,
            details=f"Created new user '{new_user.username}' with role '{new_user.role}'",
            ip_address=ip_address,
        )

        return UserResponse(
            id=new_user.id,
            username=new_user.username,
            email=new_user.email,
            full_name=new_user.full_name,
            role=new_user.role,
            department=new_user.department,
            status=new_user.status,
            is_active=new_user.is_active,
            is_admin=new_user.is_admin,
            assigned_machines=new_user.assigned_machine_ids,
            permissions=new_user.permissions_list,
            created_at=new_user.created_at,
        )

    async def get_all_users(self) -> List[UserResponse]:
        """Lists all registered platform users."""
        stmt = (
            select(User)
            .options(
                selectinload(User.roles).selectinload(Role.permissions),
                selectinload(User.assigned_machines),
            )
            .order_by(User.id)
        )
        result = await self.db.execute(stmt)
        users = result.scalars().all()
        return [
            UserResponse(
                id=u.id,
                username=u.username,
                email=u.email,
                full_name=u.full_name,
                role=u.role,
                department=u.department,
                status=u.status,
                is_active=u.is_active,
                is_admin=u.is_admin,
                assigned_machines=u.assigned_machine_ids,
                permissions=u.permissions_list,
                last_login=u.last_login,
                created_at=u.created_at,
            )
            for u in users
        ]

    async def get_all_roles(self) -> List[RoleResponse]:
        """Lists enterprise roles and their granted permissions."""
        stmt = select(Role).options(selectinload(Role.permissions)).order_by(Role.id)
        result = await self.db.execute(stmt)
        roles = result.scalars().all()
        return [RoleResponse.model_validate(r) for r in roles]

    async def get_audit_logs(
        self,
        limit: int = 50,
        offset: int = 0,
        action: Optional[str] = None,
    ) -> List[AuditLogResponse]:
        """Queries enterprise compliance audit trail."""
        stmt = select(AuditLog).order_by(desc(AuditLog.timestamp)).offset(offset).limit(limit)
        if action:
            stmt = stmt.where(AuditLog.action == action)
        result = await self.db.execute(stmt)
        logs = result.scalars().all()
        return [AuditLogResponse.model_validate(l) for l in logs]
