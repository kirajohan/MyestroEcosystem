'''C:\Projects\MyestroEco\MyestroEco\telegram_bot\backend\app\models\conversation.py'''

from datetime import datetime
from sqlalchemy import (
    Column, BigInteger, String, Boolean, Text, Integer, DateTime, ForeignKey, Index
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import uuid

class ConversationThread(Base):
    __tablename__ = "conversation_threads"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=True)
    cefr_level = Column(String(10), default="A1")
    is_active = Column(Boolean, default=True)
    telegram_thread_id = Column(BigInteger, nullable=True)
    last_sync_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="threads")
    messages = relationship("Message", back_populates="thread", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    thread_id = Column(BigInteger, ForeignKey("conversation_threads.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # ← YANGI: Session tracking for memory system
    session_id = Column(
        PG_UUID(as_uuid=True), 
        ForeignKey("ai_memory_sessions.session_id", ondelete="CASCADE"),
        nullable=True
    )
    
    role = Column(String(20), default="user")
    content = Column(Text, nullable=False)
    content_type = Column(String(20), default="text")
    ai_model = Column(String(100), nullable=True)
    tokens_used = Column(Integer, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    cefr_level = Column(String(10), nullable=True)
    grammar_corrections = Column(JSONB, nullable=True)
    vocabulary_suggestions = Column(JSONB, nullable=True)
    source = Column(String(20), default="telegram")
    
    # ← YANGI: Memory management
    is_in_memory = Column(Boolean, nullable=False, default=True)  # In Redis cache?
    memory_index = Column(Integer, nullable=True)  # Position in sliding window
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    thread = relationship("ConversationThread", back_populates="messages")
    
    # ← YANGI: Memory session relationship
    memory_session = relationship(
        "AIMemorySession",
        foreign_keys=[session_id],
        back_populates="messages"
    )

    __table_args__ = (
        Index("idx_messages_thread_id", "thread_id"),
        Index("idx_messages_user_id", "user_id"),
        Index("idx_messages_session_id", "session_id"),
        Index("idx_messages_session_created", "session_id", "created_at", postgresql_using="DESC"),
        Index("idx_messages_created_at", "created_at"),
    )