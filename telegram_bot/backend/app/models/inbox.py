"""Inbox message models — user messages sent to admin (inbox).

Phase 4: Admin inbox for receiving user messages and sending replies
- inbox_messages: main message from user
- inbox_message_history: reply thread between user and admin
"""

from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class InboxMessage(Base):
    __tablename__ = "inbox_messages"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    admin_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    subject = Column(String(255), nullable=True)
    user_message = Column(Text, nullable=False)
    admin_reply = Column(Text, nullable=True)
    status = Column(String(20), default="new")  # 'new', 'read', 'replied', 'closed'
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

# InboxMessage modeliga user relationship qo'shing
    user = relationship("User", foreign_keys=[user_id])
    admin = relationship("User", foreign_keys=[admin_id])
    history = relationship(
        "InboxMessageHistory",
        back_populates="inbox_message",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<InboxMessage {self.id} from user {self.user_id}>"


class InboxMessageHistory(Base):
    __tablename__ = "inbox_message_history"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    inbox_message_id = Column(
        BigInteger,
        ForeignKey("inbox_messages.id", ondelete="CASCADE"),
        nullable=False,
    )
    sender_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    message_text = Column(Text, nullable=False)
    message_type = Column(String(20), default="reply")  # 'user_message', 'admin_reply'
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    inbox_message = relationship("InboxMessage", back_populates="history")
    sender = relationship("User", foreign_keys=[sender_id])

    def __repr__(self) -> str:
        return f"<InboxMessageHistory {self.id} for message {self.inbox_message_id}>"