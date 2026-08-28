"""Security utilities - JWT token yaratish/tekshirish, password hashing.

⚠️ MUHIM: create_access_token va get_current_user IKKALASI HAM
bir xil ACCESS_SECRET kalitni ishlatishi SHART. Aks holda JWT ishlamaydi.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
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


def _get(name: str, default: Any = None) -> Any:
    """settings dan xavfsiz qiymat olish."""
    return getattr(settings, name, default)


# ────────────────────────────────────────────────────────────────
# YAGONA SIR KALITLAR — create VA verify ikkalasi ham SHULARNI ishlatadi!
# ────────────────────────────────────────────────────────────────
ACCESS_SECRET = (
    _get("JWT_ACCESS_SECRET")
    or _get("SECRET_KEY")
    or "change-me-in-production"
)
REFRESH_SECRET = _get("JWT_REFRESH_SECRET") or ACCESS_SECRET
ALGORITHM = _get("ALGORITHM", "HS256")
ACCESS_EXPIRE_MINUTES = (
    _get("JWT_ACCESS_EXPIRE")
    or _get("ACCESS_TOKEN_EXPIRE_MINUTES")
    or 15
)
REFRESH_EXPIRE_MINUTES = _get("JWT_REFRESH_EXPIRE") or (7 * 24 * 60)  # 7 kun


# ══════════════════════════════════════════════════════════════
# PASSWORD HASHING (bcrypt)
# ══════════════════════════════════════════════════════════════
def hash_password(password: str) -> str:
    """Parolni hash qilish (bcrypt)."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Parolni tekshirish (bcrypt)."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


# ══════════════════════════════════════════════════════════════
# JWT TOKEN YARATISH
# ══════════════════════════════════════════════════════════════
def create_access_token(
    user_id: int,
    email: Optional[str] = None,
    role: str = "student",
) -> str:
    """Access token yaratish (15 min).

    Eslatma: email ixtiyoriy, chunki Telegram userlarda email bo'lmaydi.
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_EXPIRE_MINUTES)
    payload: Dict[str, Any] = {
        "sub": str(user_id),
        "type": "access",
        "exp": expire,
    }
    if email:
        payload["email"] = email
    if role:
        payload["role"] = role
    return jwt.encode(payload, ACCESS_SECRET, algorithm=ALGORITHM)


def create_refresh_token(user_id: int) -> str:
    """Refresh token yaratish (7 kun)."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=REFRESH_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": expire,
    }
    return jwt.encode(payload, REFRESH_SECRET, algorithm=ALGORITHM)


def verify_token(token: str, secret: str) -> Dict[str, Any]:
    """Tokenni decode qilish. Payload qaytaradi yoki ValueError."""
    try:
        return jwt.decode(token, secret, algorithms=[ALGORITHM])
    except JWTError as e:
        raise ValueError(f"Invalid token: {e}")


# ══════════════════════════════════════════════════════════════
# DEPENDENCIES
# ══════════════════════════════════════════════════════════════
async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """JWT token'dan foydalanuvchini olish.

    ⚠️ BU YERDA ACCESS_SECRET ishlatiladi — create_access_token bilan BIR XIL!
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token taqdim etilmagan",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        payload = jwt.decode(token, ACCESS_SECRET, algorithms=[ALGORITHM])
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

    result = await db.execute(select(User).where(User.id == user_id))
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