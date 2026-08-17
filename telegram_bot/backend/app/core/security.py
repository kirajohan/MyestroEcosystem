"""Security utilities - JWT token yaratish/tekshirish, password hashing."""
"""Security utilities - JWT token yaratish/tekshirish, password hashing."""

from datetime import datetime, timedelta, timezone
from typing import Optional , Dict , Any

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.user import User


# ══════════════════════════════════════════════════════════════
# GLOBALS
# ══════════════════════════════════════════════════════════════
security = HTTPBearer(auto_error=False)

SECRET_KEY = getattr(settings, "SECRET_KEY", "change-me-in-production")
ALGORITHM = getattr(settings, "ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = getattr(settings, "ACCESS_TOKEN_EXPIRE_MINUTES", 15)


# ══════════════════════════════════════════════════════════════
# PASSWORD HASHING (bcrypt — passlib emas)
# ══════════════════════════════════════════════════════════════
def hash_password(password: str) -> str:
    """Parolni hash qilish (bcrypt)."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Parolni tekshirish (bcrypt)."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except (ValueError, TypeError):
        return False


# ══════════════════════════════════════════════════════════════
# JWT TOKEN YARATISH
# ══════════════════════════════════════════════════════════════
def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Access token yaratish."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ══════════════════════════════════════════════════════════════
# DEPENDENCIES
# ══════════════════════════════════════════════════════════════
async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """JWT token'dan foydalanuvchini olish."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token taqdim etilmagan",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token yaroqsiz",
            )
        user_id = int(user_id)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token yaroqsiz",
        )
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token yaroqsiz format",
        )

    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Foydalanuvchi topilmadi",
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Faol foydalanuvchini olish."""
    if hasattr(current_user, "is_active") and not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Foydalanuvchi faol emas",
        )
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Admin foydalanuvchini olish."""
    role = getattr(current_user, "role", None)
    if role not in ("admin", "superadmin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin huquqi talab qilinadi",
        )
    return current_user
    

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except (ValueError, TypeError):
        return False


def create_access_token(user_id: int, email: str, role: str) -> str:
    """Create JWT access token (15 min)."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_ACCESS_EXPIRE)
    payload = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "type": "access",
        "exp": expire,
    }
    return jwt.encode(payload, settings.JWT_ACCESS_SECRET, algorithm="HS256")


def create_refresh_token(user_id: int) -> str:
    """Create JWT refresh token (7 days)."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_REFRESH_EXPIRE)
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": expire,
    }
    return jwt.encode(payload, settings.JWT_REFRESH_SECRET, algorithm="HS256")


def verify_token(token: str, secret: str) -> Dict[str, Any]:
    """Decode and validate JWT token. Returns payload or raises."""
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        return payload
    except JWTError as e:
        raise ValueError(f"Invalid token: {str(e)}")
