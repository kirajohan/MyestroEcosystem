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
    
    # Eslatma matni
    text = Column(Text, nullable=False)
    
    # Turi: once (bir martalik), daily (har kuni), weekly (har hafta)
    reminder_type = Column(String(20), nullable=False, default="once")
    
    # Bir martalik uchun aniq datetime (UTC)
    due_at = Column(DateTime(timezone=True), nullable=False)
    
    # Daily/Weekly uchun vaqt (HH:MM)
    scheduled_time = Column(String(5), nullable=True)  # "15:00"
    
    # Weekly uchun haftaning kuni (0=Monday, 6=Sunday)
    day_of_week = Column(Integer, nullable=True)
    
    # Holat
    is_active = Column(Boolean, default=True, nullable=False)
    last_sent_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    
    # Relationship
    user = relationship("User", backref="reminders")

    def __repr__(self):
        return f"<Reminder {self.id} type={self.reminder_type} user={self.user_id}>"