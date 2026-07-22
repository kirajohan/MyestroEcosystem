from pydantic import BaseModel, EmailStr
from typing import Optional , List
from datetime import datetime

class UserAIToggleRequest(BaseModel):
    """Request body for toggling user AI status."""
    ai_enabled: bool


class SystemSettingResponse(BaseModel):
    """Response model for system settings."""
    key: str
    value: str
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class SystemSettingUpdateRequest(BaseModel):
    """Request body for updating system settings."""
    value: str


class AdminLoginRequest(BaseModel):
    email: str
    password: str


class UserCreate(BaseModel):
    email: str
    password: Optional[str] = None
    full_name: str
    role: str = "student"
    cefr_level: str = "A1"
    target_level: str = "B1"
    lang: str = "uz"
    auth_provider: str = "email"
    provider_user_id: Optional[str] = None
    telegram_id: Optional[int] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    cefr_level: Optional[str] = None
    target_level: Optional[str] = None
    lang: Optional[str] = None
    phone: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    cefr_level: str
    target_level: str
    lang: str
    is_active: bool
    is_verified: bool
    profile_completed: bool
    telegram_id: Optional[int] = None
    telegram_username: Optional[str] = None
    auth_provider: str
    avatar_url: Optional[str] = None
    phone: Optional[str] = None
    ai_enabled: bool = True
    last_login_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    email: str
    password: str


class OTPSendRequest(BaseModel):
    email: str


class OTPVerifyRequest(BaseModel):
    email: str
    code: str


class GoogleAuthRequest(BaseModel):
    token: str


class TelegramAuthRequest(BaseModel):
    id: int
    first_name: str
    username: Optional[str] = None
    photo_url: Optional[str] = None
    auth_date: int
    hash: str


class UsersListResponse(BaseModel):
    data: List[UserResponse]
    total: int

# Admin login response — JWT token bilan
class AdminLoginResponse(BaseModel):
    success: bool
    user: UserResponse
    access_token: Optional[str] = None  # JWT access token (admin panel uchun)
