# app/services/auth_service.py — TO'LIQ QAYTA YOZILGAN

import random
import hashlib
import hmac
import sys
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session as DBSession
from redis import Redis
from app.config import settings
from app.core.security import (
    hash_password, verify_password,
)
from app.models.user import User
from app.core.exceptions import UnauthorizedException, ConflictException, ForbiddenException
from app.schemas.phone import normalize_phone  # avvalgi javobda bergan fayl


def authenticate_user(db: DBSession, email: str, password: str) -> User:
    user = db.query(User).filter(User.email == email, User.is_active == True).first()
    if not user or not user.password_hash:
        raise UnauthorizedException("Invalid email or password")
    if not verify_password(password, user.password_hash):
        raise UnauthorizedException("Invalid email or password")
    return user


def authenticate_admin(db: DBSession, email: str, password: str) -> dict:
    from app.core.security import create_access_token, hash_password
    
    user = db.query(User).filter(User.email == email, User.is_active == True).first()
    if not user or not user.password_hash:
        raise UnauthorizedException("Invalid email or password")

    # --- УМНАЯ ПРОВЕРКА И АВТО-ИСПРАВЛЕНИЕ ПАРОЛЕЙ ---
    # Хэши bcrypt всегда начинаются с $ (например, $2b$12$...)
    if not user.password_hash.startswith("$"):
        # Если пароль в базе не начинается с $, значит это обычный текст
        if user.password_hash == password:
            # Пароль верный! Хэшируем его и сохраняем, чтобы починить базу навсегда
            user.password_hash = hash_password(password)
            db.commit()
            db.refresh(user)
        else:
            raise UnauthorizedException("Invalid email or password")
    else:
        # Если в базе нормальный хэш, проверяем стандартным способом
        if not verify_password(password, user.password_hash):
            raise UnauthorizedException("Invalid email or password")
    # -------------------------------------------------

    if user.role not in ["admin", "superadmin"]:
        raise ForbiddenException("Admin access required")

    # Generate JWT access token for admin panel
    access_token = create_access_token(user.id, user.email, user.role)
    return {"user": user, "access_token": access_token}



def register_user(db: DBSession, user_data: dict) -> User:
    email = user_data["email"]
    phone_input = user_data.get("phone")
    
    print(f"[REGISTER] phone_input={phone_input}", file=sys.stderr)
    
    phone = normalize_phone(phone_input) if phone_input else None
    print(f"[REGISTER] normalized phone={phone}", file=sys.stderr)
    
    phone = phone or phone_input
    print(f"[REGISTER] final phone={phone}", file=sys.stderr)
    
    telegram_id = user_data.get("telegram_id")

    # Check if telegram_id already exists — UPDATE instead of ERROR
    if telegram_id:
        existing_tg = db.query(User).filter(User.telegram_id == telegram_id).first()
        if existing_tg:
            # Update existing user
            existing_tg.email = email
            existing_tg.full_name = user_data["full_name"]
            existing_tg.phone = phone
            existing_tg.cefr_level = user_data.get("cefr_level", existing_tg.cefr_level or "A1")
            existing_tg.lang = user_data.get("lang", existing_tg.lang or "uz")
            if user_data.get("password"):
                existing_tg.password_hash = hash_password(user_data["password"])
            db.commit()
            db.refresh(existing_tg)
            return existing_tg

    existing_email = db.query(User).filter(User.email == email).first()
    if existing_email:
        raise ConflictException("Email already registered")
    if phone:
        existing_phone = db.query(User).filter(User.phone == phone).first()
        if existing_phone:
            raise ConflictException("Phone already registered")

    user = User(
        email=email,
        password_hash=hash_password(user_data["password"]) if user_data.get("password") else None,
        full_name=user_data["full_name"],
        role=user_data.get("role", "student"),
        cefr_level=user_data.get("cefr_level", "A1"),
        target_level=user_data.get("target_level", "B1"),
        lang=user_data.get("lang", "uz"),
        auth_provider=user_data.get("auth_provider", "email"),
        phone=phone,
        telegram_id=telegram_id,
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
    # ⚠️ ASOSIY TUZATISH — dublikat/mos kelmagan formatlarni bir joyda hal qiladi
    phone = normalize_phone(phone) or phone
    user = db.query(User).filter(User.phone == phone, User.is_active == True).first()
    if user:
        return True, {
            "id": user.id, "email": user.email,
            "full_name": user.full_name, "phone": user.phone,
            "telegram_id": user.telegram_id,
        }
    return False, {}


def authenticate_by_phone(db: DBSession, phone: str, telegram_id: int, password: str = None) -> Optional[User]:
    phone = normalize_phone(phone) or phone
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
