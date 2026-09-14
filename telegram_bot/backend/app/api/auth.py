# app/routers/auth.py — TO'LIQ QAYTA YOZILGAN

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DBSession
from redis import Redis
from app.database import get_db
from app.config import settings
from app.schemas.user import (
    UserCreate, LoginRequest, UserResponse,
    OTPSendRequest, OTPVerifyRequest,
    TelegramAuthRequest, AdminLoginRequest, AdminLoginResponse,
)
from app.services import auth_service
from app.models.user import User
from app.core.exceptions import UnauthorizedException, ConflictException
from app.schemas.phone import normalize_phone
import redis as redis_lib

router = APIRouter(prefix="/api/auth", tags=["auth"])


def get_redis() -> Redis:
    return redis_lib.from_url(settings.REDIS_URL, decode_responses=False)


@router.post("/register", response_model=AdminLoginResponse)
def register(data: UserCreate, db: DBSession = Depends(get_db)):
    user = auth_service.register_user(db, data.model_dump())
    return AdminLoginResponse(success=True, user=UserResponse.model_validate(user))


@router.post("/login", response_model=AdminLoginResponse)
def login(data: LoginRequest, db: DBSession = Depends(get_db)):
    user = auth_service.authenticate_user(db, data.email, data.password)
    return AdminLoginResponse(success=True, user=UserResponse.model_validate(user))


@router.post("/admin-login", response_model=AdminLoginResponse)
def admin_login(data: AdminLoginRequest, db: DBSession = Depends(get_db)):
    result = auth_service.authenticate_admin(db, data.email, data.password)
    return AdminLoginResponse(
        success=True,
        user=UserResponse.model_validate(result["user"]),
        access_token=result.get("access_token"),
        refresh_token=result.get("refresh_token"),  # ← YANGI
    )

@router.post("/otp/send")
def send_otp(data: OTPSendRequest, r: Redis = Depends(get_redis)):
    code = auth_service.generate_otp(data.email, r)
    return {"message": "OTP sent"}


@router.post("/otp/verify")
def verify_otp(data: OTPVerifyRequest, r: Redis = Depends(get_redis)):
    valid = auth_service.verify_otp(data.email, data.code, r)
    if not valid:
        raise UnauthorizedException("Invalid OTP")
    return {"message": "OTP verified"}


@router.post("/telegram", response_model=AdminLoginResponse)
def telegram_auth(data: TelegramAuthRequest, db: DBSession = Depends(get_db)):
    valid = auth_service.verify_telegram_hash(data.model_dump(), settings.BOT_TOKEN)
    if not valid:
        raise UnauthorizedException("Invalid Telegram auth data")
    user = db.query(User).filter(User.telegram_id == data.id).first()
    if not user:
        user = auth_service.register_user(db, {
            "email": f"tg_{data.id}@placeholder.com",
            "full_name": data.first_name,
            "auth_provider": "telegram",
            "provider_user_id": str(data.id),
            "telegram_id": data.id,
        })
    return AdminLoginResponse(success=True, user=UserResponse.model_validate(user))

@router.post("/register-init", response_model=AdminLoginResponse)
def register_init(data: dict, db: DBSession = Depends(get_db)):
    email = data.get("email", "")
    if not email:
        raise UnauthorizedException("Email required")
    user = auth_service.register_user(db, {         
        "email": email,
        "password": data.get("password", ""),
        "full_name": data.get("full_name", ""),
        "phone": data.get("phone"),
        "telegram_id": data.get("telegram_id"),
        "auth_provider": "email",
    })
    return AdminLoginResponse(success=True, user=UserResponse.model_validate(user))


@router.post("/check-phone")
def check_phone(data: dict, db: DBSession = Depends(get_db)):
    phone = data.get("phone", "")
    if not phone:
        return {"exists": False, "user": {}}
    exists, user_info = auth_service.check_phone_exists(db, phone)
    return {"exists": exists, "user": user_info}


@router.post("/phone-login", response_model=AdminLoginResponse)
def phone_login(data: dict, db: DBSession = Depends(get_db)):
    phone = data.get("phone", "").strip()
    password = data.get("password", "")
    telegram_id = data.get("telegram_id")
    
    if not phone:
        raise UnauthorizedException("Telefon raqami majburiy")
    
    # Phone formatni normalize qilish
    clean_phone = phone.replace("+", "").replace(" ", "").replace("-", "")
    
    if len(clean_phone) == 9:
        clean_phone = "998" + clean_phone
    elif len(clean_phone) == 12 and clean_phone.startswith("998"):
        pass
    elif clean_phone.startswith("8") and len(clean_phone) == 10:
        clean_phone = "998" + clean_phone[1:]
    
    # Telefon bo'yicha foydalanuvchini topish
    user = db.query(User).filter(
        (User.phone == clean_phone) | 
        (User.phone == phone) |
        (User.phone == "+" + clean_phone)
    ).first()
    
    if not user:
        raise UnauthorizedException("Bu telefon raqami royxatdan otmagan")
    
    # Admin panel uchun - parol tekshirish
    if telegram_id is None and password:
        if user.role not in ('admin', 'superadmin'):
            raise UnauthorizedException("Bu tizimga faqat adminlar kira oladi")
        
        from app.core.security import verify_password
        if not user.password_hash or not verify_password(password, user.password_hash):
            raise UnauthorizedException("Parol notogri")
        
        # ✅ auth_service orqali token yaratish
        result = auth_service.authenticate_admin(db, user.email, password)
        
        return AdminLoginResponse(
            success=True,
            user=UserResponse.model_validate(user),
            access_token=result.get("access_token"),
            refresh_token=result.get("refresh_token"),
        )
    
    # Telegram bot uchun
    user = auth_service.authenticate_by_phone(db, phone, telegram_id, password)
    if not user:
        raise UnauthorizedException("User not found with this phone or wrong password")
    return AdminLoginResponse(success=True, user=UserResponse.model_validate(user))




@router.post("/refresh", response_model=AdminLoginResponse)
def refresh_token(data: dict, db: DBSession = Depends(get_db)):
    """Refresh token orqali yangi access token olish"""
    refresh_token = data.get("refresh_token")
    if not refresh_token:
        raise UnauthorizedException("Refresh token majburiy")
    
    result = auth_service.refresh_access_token(db, refresh_token)
    if not result:
        raise UnauthorizedException("Refresh token yaroqsiz")
    
    return AdminLoginResponse(
        success=True,
        user=UserResponse.model_validate(result["user"]),
        access_token=result["access_token"],
        refresh_token=result.get("refresh_token"),
    )