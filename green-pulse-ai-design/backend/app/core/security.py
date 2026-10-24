"""
GreenPulse AI - Industrial Security & Authentication
Handles password hashing (bcrypt), JWT generation, refresh tokens, and audit verification.
"""
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Union
import hashlib
import hmac
import secrets
import bcrypt
from jose import jwt, JWTError

from app.core.config import settings


def hash_password(password: str) -> str:
    """Computes standard bcrypt hash with salt."""
    pwd_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies plain password against stored hash using constant-time comparison.
    Supports standard bcrypt as well as legacy salted SHA-256 hashes for seamless migration.
    """
    if not hashed_password:
        return False
    if hashed_password.startswith("$2b$") or hashed_password.startswith("$2a$"):
        pwd_bytes = plain_password.encode("utf-8")[:72]
        return bcrypt.checkpw(pwd_bytes, hashed_password.encode("utf-8"))
    
    # Fallback legacy salted SHA-256
    legacy_salt = settings.SECRET_KEY[:16]
    expected_hash = hashlib.sha256(f"{legacy_salt}{plain_password}".encode("utf-8")).hexdigest()
    return hmac.compare_digest(expected_hash, hashed_password)


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Encodes JWT access token with role, permissions, and expiration claims."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": now,
        "type": "access",
    })
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Encodes cryptographic JWT refresh token."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
    to_encode.update({
        "exp": expire,
        "iat": now,
        "jti": secrets.token_urlsafe(32),
        "type": "refresh",
    })
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """Decodes and validates JWT signature and expiration claims."""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


def hash_token(token: str) -> str:
    """Computes SHA-256 hash of refresh token for database indexation."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def generate_audit_hash(payload_str: str) -> str:
    """Generates cryptographic SHA-256 checksum for audit logs and reports."""
    return f"SHA256:{hashlib.sha256(payload_str.encode('utf-8')).hexdigest()[:16]}"
