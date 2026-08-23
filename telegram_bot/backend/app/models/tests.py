# telegram_bot/backend/models/tests.py
"""
Test moduli uchun SQLAlchemy modellar.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, BigInteger, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.database import Base


class Test(Base):
    __tablename__ = 'tests'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    cefr_level = Column(String(2), nullable=False)  # A1, A2, B1, B2, C1, C2
    passing_score = Column(Integer, nullable=False, default=60)
    is_active = Column(Boolean, nullable=False, default=True)
    total_duration = Column(Integer, nullable=False, default=30)  # minutes
    max_score = Column(Integer, nullable=True)
    status = Column(String(50), nullable=False, default='active')  # draft, published, active, archived
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class TestQuestion(Base):
    __tablename__ = 'test_questions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    test_id = Column(Integer, ForeignKey('tests.id', ondelete='CASCADE'), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), nullable=False, default='multiple_choice')
    options = Column(JSONB, nullable=False)  # [{"label": "...", "is_correct": bool}, ...]
    correct_answer = Column(String(500), nullable=False)  # The correct option label
    explanation = Column(Text, nullable=True)
    points = Column(Integer, nullable=False, default=1)
    difficulty = Column(String(20), nullable=False, default='medium')  # easy, medium, hard
    order_index = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class TestAttempt(Base):
    __tablename__ = 'test_attempts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)  # Telegram user ID
    test_id = Column(Integer, ForeignKey('tests.id', ondelete='CASCADE'), nullable=False)
    score = Column(Integer, nullable=False)
    total_questions = Column(Integer, nullable=False)
    percentage = Column(Integer, nullable=False)
    passed = Column(Boolean, nullable=False)
    finished_at = Column(DateTime(timezone=True), server_default=func.now())
