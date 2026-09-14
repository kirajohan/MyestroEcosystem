"""
Eslatmalar (Reminders) modeli.
User'lar tomonidan yaratiladigan vaqtli xabarlar.
"""
from datetime import datetime
from sqlalchemy import (
    Column, BigInteger, String, Text, DateTime, Boolean, 
    ForeignKey, Integer, Time
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    is_ai_generated = Column(Boolean, default=False, nullable=False)
    
    # AI prompt (agar is_ai_generated=True bo'lsa)
    ai_prompt = Column(Text, nullable=True)
    
    # Oddiy statik matn (agar is_ai_generated=False bo'lsa)
    text = Column(Text, nullable=False)
    
    reminder_type = Column(String(20), nullable=False, default="once")
    due_at = Column(DateTime(timezone=True), nullable=False)
    scheduled_time = Column(String(5), nullable=True)
    day_of_week = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    last_sent_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    user = relationship("User", backref="reminders")

    def __repr__(self):
        return f"<Reminder {self.id} type={self.reminder_type} user={self.user_id}>"