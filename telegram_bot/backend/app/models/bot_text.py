"""Bot text (CMS) model — manage bot messages from admin panel."""

from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Text, DateTime
from sqlalchemy.sql import func
from app.database import Base


class BotText(Base):
    __tablename__ = "bot_texts"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    key = Column(String(100), nullable=False)  # "video.not_found", "profile.title"
    lang = Column(String(10), default="uz", nullable=False)
    text = Column(Text, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        # Unique constraint: one text per key+lang combination
        # (use raw SQL if your DB doesn't support this in __table_args__)
    )

    def __repr__(self) -> str:
        return f"<BotText {self.key} {self.lang}>"
