import uuid
from datetime import datetime
from sqlalchemy import (
    Column, BigInteger, String, Boolean, Text, DateTime, ForeignKey, UUID
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)
    full_name = Column(String(255), nullable=False)
    role = Column(String(20), default="student")
    cefr_level = Column(String(10), default="A1")
    target_level = Column(String(10), default="B1")
    avatar_url = Column(Text, nullable=True)
    phone = Column(String(50), nullable=True)
    lang = Column(String(10), default="uz")
    learning_lang = Column(String(10), default="en")
    telegram_id = Column(BigInteger, unique=True, nullable=True, index=True)
    telegram_username = Column(String(255), nullable=True)
    auth_provider = Column(String(20), default="email")
    provider_user_id = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    profile_completed = Column(Boolean, default=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    location = Column(String(255), nullable=True)
    ai_enabled = Column(Boolean, default=True, nullable=False,
                        comment="Foydalanuvchi uchun AI agent yoqilganmi")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    threads = relationship("ConversationThread", back_populates="user", cascade="all, delete-orphan")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    refresh_token = Column(String(500))
    device_info = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_revoked = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="sessions")