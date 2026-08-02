"""Inbox models for admin-to-user messaging system."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.database import Base


class InboxMessage(Base):
    """Main inbox message from user."""
    
    __tablename__ = "inbox_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    subject = Column(String(255), nullable=True)
    user_message = Column(Text, nullable=False)
    admin_reply = Column(Text, nullable=True)
    status = Column(String(50), default="new", index=True)  # new, read, replied, closed
    is_read = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="inbox_messages")
    history = relationship("InboxMessageHistory", back_populates="inbox_message", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<InboxMessage id={self.id} user_id={self.user_id} status={self.status}>"


class InboxMessageHistory(Base):
    """Message history/thread for inbox messages."""
    
    __tablename__ = "inbox_message_history"
    
    id = Column(Integer, primary_key=True, index=True)
    inbox_message_id = Column(Integer, ForeignKey("inbox_messages.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    message_text = Column(Text, nullable=False)
    message_type = Column(String(50), default="user_message")  # user_message, admin_reply
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    inbox_message = relationship("InboxMessage", back_populates="history")
    sender = relationship("User")
    
    def __repr__(self):
        return f"<InboxMessageHistory id={self.id} inbox_id={self.inbox_message_id} type={self.message_type}>"
