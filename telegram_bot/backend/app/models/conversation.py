from datetime import datetime
from sqlalchemy import (
    Column, BigInteger, String, Boolean, Text, Integer, DateTime, ForeignKey, Index
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


# /backend/app/models/conversation.py

from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey, Boolean
from datetime import datetime

class ConversationThread(Base):
    """
    THREADED MODE uchun minimal model
    Faqat metadata saqlanadi — messages Telegram'dan olinadi
    """
    __tablename__ = "conversation_threads"
    
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    telegram_topic_id = Column(BigInteger, nullable=False, unique=True)  # ⭐ KEY!
    topic_title = Column(String(255), nullable=True)
    cefr_level = Column(String(10), default="A1")
    is_active = Column(Boolean, default=True)
    last_message_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="threads")


class Message(Base):
    """
    Message model for storing conversation messages
    """
    __tablename__ = "messages"
    
    id = Column(BigInteger, primary_key=True)
    thread_id = Column(BigInteger, ForeignKey("conversation_threads.id"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    telegram_message_id = Column(BigInteger, nullable=True)
    content = Column(Text, nullable=False)
    sender = Column(String(50), default="user")  # 'user' or 'assistant'
    created_at = Column(DateTime, default=datetime.utcnow)
