import hashlib
import hmac
import logging
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import User

load_dotenv()

logger = logging.getLogger(__name__)

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:  # pragma: no cover
    raise RuntimeError(
        "SECRET_KEY environment variable is not set. "
        "Set it in backend/.env or as an environment variable. "
        'Generate one with: python -c "import secrets; print(secrets.token_hex(32))"'
    )
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def hash_api_key(api_key: str) -> str:
    """Hash an API key using HMAC-SHA256 for secure storage"""
    return hmac.new(SECRET_KEY.encode(), api_key.encode(), hashlib.sha256).hexdigest()


def hash_token(token: str) -> str:
    """Hash a token (reset tokens, etc.) using HMAC-SHA256"""
    return hmac.new(SECRET_KEY.encode(), token.encode(), hashlib.sha256).hexdigest()


def _get_user_from_jwt(token: str, db: Session) -> User:
    """Decode JWT token and return the associated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Get the current authenticated user (JWT only)"""
    return _get_user_from_jwt(credentials.credentials, db)


def get_current_active_user(current_user: User = Depends(get_current_user)):
    """Ensure user is active"""
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user account")
    return current_user


def get_current_admin_user(current_user: User = Depends(get_current_active_user)):
    """Ensure user is an admin"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required"
        )
    return current_user


def generate_password_reset_token() -> str:
    """Generate a secure random token for password reset"""
    return secrets.token_urlsafe(32)


def create_password_reset_token(user: User, db: Session) -> str:
    """Create and store password reset token (hashed)"""
    token = generate_password_reset_token()
    expires = datetime.now(timezone.utc) + timedelta(hours=24)

    user.password_reset_token = hash_token(token)
    user.password_reset_expires = expires
    db.commit()

    return token


def verify_reset_token(token: str, db: Session) -> Optional[User]:
    """Verify password reset token and return user if valid"""
    token_hash = hash_token(token)
    user = (
        db.query(User)
        .filter(
            User.password_reset_token == token_hash,
            User.password_reset_expires > datetime.now(timezone.utc),
        )
        .first()
    )

    return user


def generate_api_key() -> str:
    """Generate a secure random API key"""
    return f"crm_{secrets.token_hex(24)}"


def get_user_from_api_key(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Get user from API key if the token is an API key"""
    try:
        token = credentials.credentials
        if token.startswith("crm_"):
            key_hash = hash_api_key(token)
            user = db.query(User).filter(User.api_key_hash == key_hash).first()
            if user and user.is_active:
                return user
        return None
    except Exception:
        return None


def get_current_user_or_api_key(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Get the current authenticated user (via JWT or API key)"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials

    # Try API key authentication first
    if token.startswith("crm_"):
        key_hash = hash_api_key(token)
        user = db.query(User).filter(User.api_key_hash == key_hash).first()
        if user and user.is_active:
            return user
        raise credentials_exception

    # Fall back to JWT authentication
    return _get_user_from_jwt(token, db)


def validate_password(password: str) -> None:
    """Validate password meets minimum requirements. Raises HTTPException if invalid."""
    if len(password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long",
        )
