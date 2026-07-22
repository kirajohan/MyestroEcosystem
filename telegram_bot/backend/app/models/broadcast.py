"""Broadcast models — broadcast_jobs and broadcast_history tables."""

from sqlalchemy import Column, BigInteger, String, Text, Integer, DateTime, ForeignKey, ARRAY
from sqlalchemy.sql import func
from app.database import Base


class BroadcastJob(Base):
    """Broadcast job — created by admin, processed by bot worker."""
    __tablename__ = "broadcast_jobs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_by_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)  # HTML formatted
    message_type = Column(String(20), default="text")  # text, photo, video, document
    file_id = Column(String(255), nullable=True)  # Telegram file_id for media
    target_users = Column(ARRAY(BigInteger), default=[])  # Array of user IDs
    scheduled_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(20), default="pending")  # pending, queued, sending, completed, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    total_users = Column(Integer, default=0)
    sent_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)


class BroadcastHistory(Base):
    """Broadcast delivery history — per-user delivery status."""
    __tablename__ = "broadcast_history"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    broadcast_job_id = Column(BigInteger, ForeignKey("broadcast_jobs.id", ondelete="CASCADE"), nullable=False)
    recipient_user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    message_telegram_id = Column(BigInteger, nullable=True)  # Telegram message ID if successfully sent
    status = Column(String(20), default="pending")  # pending, sent, failed
    error_message = Column(Text, nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())