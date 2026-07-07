import random
import hashlib
import hmac
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session as DBSession
from redis import Redis
from app.config import settings
from app.core.security import (
    hash_password, verify_password,
    # Token yaratish hozircha kerak emas
    # create_access_token, create_refresh_token,
    # verify_token,
)
from app.models.user import User  # Session modeli kerak emas
from app.core.exceptions import UnauthorizedException, ConflictException, ForbiddenException
# from datetime import datetime, timedelta, timezone  # token uchun kerak edi


def authenticate_user(db: DBSession, email: str, password: str) -> User:
    user = db.query(User).filter(User.email == email, User.is_active == True).first()
    if not user or not user.password_hash:
        raise UnauthorizedException("Invalid email or password")
    if not verify_password(password, user.password_hash):
        raise UnauthorizedException("Invalid email or password")
    return user


def authenticate_admin(db: DBSession, email: str, password: str) -> dict:
    """Admin tekshiradi, lekin endi token yaratmaydi. Faqat user qaytaradi."""
    user = db.query(User).filter(User.email == email, User.is_active == True).first()
    if not user or not user.password_hash:
        raise UnauthorizedException("Invalid email or password")
    if not verify_password(password, user.password_hash):
        raise UnauthorizedException("Invalid email or password")
    if user.role not in ["admin", "superadmin"]:
        raise ForbiddenException("Admin access required")
    # Tokensiz: faqat user qaytaramiz
    return {"user": user}


# ========== TOKEN FUNKSIYALAR (hozircha izohda) ==========
# def create_user_session(db, user_id, device_info=None, ip=None):
#     """JWT yaratish. Tokensiz tizimda kerak emas."""
#     ...
#
# def refresh_user_session(db, refresh_token):
#     """Refresh tokenni yangilash. Hozircha o'chirilgan."""
#     ...
# =========================================================


def register_user(db: DBSession, user_data: dict) -> User:
    existing = db.query(User).filter(User.email == user_data["email"]).first()
    if existing:
        raise ConflictException("Email already registered")

    user = User(
        email=user_data["email"],
        password_hash=hash_password(user_data["password"]) if user_data.get("password") else None,
        full_name=user_data["full_name"],
        role=user_data.get("role", "student"),
        cefr_level=user_data.get("cefr_level", "A1"),
        target_level=user_data.get("target_level", "B1"),
        lang=user_data.get("lang", "uz"),
        auth_provider=user_data.get("auth_provider", "email"),
        phone=user_data.get("phone"),
        telegram_id=user_data.get("telegram_id"),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def generate_otp(email: str, redis_client: Redis) -> str:
    code = f"{random.randint(100000, 999999)}"
    redis_client.setex(f"otp:{email}", 300, code)
    return code


def verify_otp(email: str, code: str, redis_client: Redis) -> bool:
    stored = redis_client.get(f"otp:{email}")
    if stored and stored.decode() == code:
        redis_client.delete(f"otp:{email}")
        return True
    return False


def verify_telegram_hash(data: Dict[str, Any], bot_token: str) -> bool:
    data_copy = data.copy()
    check_hash = data_copy.pop("hash", "")
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(data_copy.items()))
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    return computed_hash == check_hash


def check_email_exists(db: DBSession, email: str) -> tuple[bool, Dict[str, Any]]:
    user = db.query(User).filter(User.email == email, User.is_active == True).first()
    if user:
        return True, {
            "id": user.id, "email": user.email,
            "full_name": user.full_name, "phone": user.phone,
            "telegram_id": user.telegram_id,
        }
    return False, {}


def check_phone_exists(db: DBSession, phone: str) -> tuple[bool, Dict[str, Any]]:
    user = db.query(User).filter(User.phone == phone, User.is_active == True).first()
    if user:
        return True, {
            "id": user.id, "email": user.email,
            "full_name": user.full_name, "phone": user.phone,
            "telegram_id": user.telegram_id,
        }
    return False, {}


def authenticate_by_phone(db: DBSession, phone: str, telegram_id: int, password: str = None) -> Optional[User]:
    user = db.query(User).filter(
        User.phone == phone,
        User.telegram_id == telegram_id,
        User.is_active == True,
    ).first()
    if not user:
        return None
    if password and user.password_hash:
        if not verify_password(password, user.password_hash):
            return None
    return user