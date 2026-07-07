"""Content model — Video / File / Text lessons for Myestro Bot."""

from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Boolean, Text, Integer, DateTime
from sqlalchemy.sql import func
from app.database import Base


class ContentItem(Base):
    __tablename__ = "content_items"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    content_type = Column(String(20), nullable=False)  # "video" yoki "file"
    file_path = Column(String(500), nullable=True)
    telegram_file_id = Column(String(255), nullable=True)  # Telegram file_id for direct send
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<ContentItem {self.id} {self.content_type} {self.title}>"
