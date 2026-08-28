"""AI Memory System models — chat sessions and context management."""

from datetime import datetime, timedelta, timezone
from sqlalchemy import Column, BigInteger, String, Boolean, Text, Integer, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql import func
from app.database import Base
import uuid

class AIMemorySession(Base):
    """User's AI chat session with context and history tracking."""
    
    __tablename__ = "ai_memory_sessions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_id = Column(PG_UUID(as_uuid=True), unique=True, default=uuid.uuid4, nullable=False)
    
    # Session metadata
    title = Column(String(255), nullable=True)
    language = Column(String(10), nullable=False, default="uz")
    cefr_level = Column(String(10), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_activity_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    # Memory management
    message_count = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Context summary
    context_summary = Column(Text, nullable=True)
    summary_generated_at = Column(DateTime(timezone=True), nullable=True)
    
    # ✅ TOZALANDI: Message bilan relationship o'chirildi, chunki Message endi faqat ConversationThread ga tegishli.
    
    __table_args__ = (
        Index("idx_ai_memory_sessions_user_id", "user_id"),
        Index("idx_ai_memory_sessions_expires_at", "expires_at"),
        Index("idx_ai_memory_sessions_last_activity", "last_activity_at", postgresql_using="DESC"),
        Index("idx_ai_memory_sessions_user_active", "user_id", "is_active", unique=True),
    )
    
    def is_expired(self) -> bool:
        if not self.expires_at:
            return False
        now = datetime.now(timezone.utc)
        expires_at = self.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        return now >= expires_at
    
    @staticmethod
    def create_new(user_id: int, language: str = "uz", cefr_level: str = None) -> "AIMemorySession":
        return AIMemorySession(
            user_id=user_id,
            language=language,
            cefr_level=cefr_level,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
            title=f"Chat Session - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )