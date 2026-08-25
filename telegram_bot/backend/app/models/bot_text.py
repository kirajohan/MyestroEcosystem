"""Bot text (CMS) model — manage bot messages from admin panel."""

from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Text, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from app.database import Base


class BotText(Base):
    __tablename__ = "bot_texts"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    key = Column(String(100), nullable=False, index=True)  # index qo'shildi
    lang = Column(String(10), default="uz", nullable=False, index=True)  # index qo'shildi
    text = Column(Text, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('key', 'lang', name='uq_bot_text_key_lang'),
    )

    def __repr__(self) -> str:
        return f"<BotText {self.key} {self.lang}>"