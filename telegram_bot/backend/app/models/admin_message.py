"""Admin message model — store user messages sent to admin (inbox)."""

from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class AdminMessage(Base):
    __tablename__ = "admin_messages"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    user_telegram_id = Column(BigInteger, nullable=True)
    user_name = Column(String(255), nullable=True)
    content_type = Column(String(20), default="text")  # text, photo, voice, document, video, sticker
    text = Column(Text, nullable=True)
    file_id = Column(String(255), nullable=True)  # Telegram file_id for media
    is_read = Column(Boolean, default=False)
    is_replied = Column(Boolean, default=False)
    admin_reply = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"<AdminMessage {self.id} from {self.user_name}>"
