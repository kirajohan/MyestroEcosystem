from datetime import datetime
from sqlalchemy import (
    Column, BigInteger, String, Boolean, Text, Integer, DECIMAL,
    DateTime, ForeignKey, UniqueConstraint, Index
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Exam(Base):
    __tablename__ = "exams"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    cefr_level = Column(String(10), nullable=False)
    status = Column(String(20), default="draft")
    total_duration = Column(Integer, default=0)
    reading_duration = Column(Integer, default=0)
    listening_duration = Column(Integer, default=0)
    speaking_duration = Column(Integer, default=0)
    writing_duration = Column(Integer, default=0)
    ownership_type = Column(String(20), default="owned")
    partner_name = Column(String(255), nullable=True)
    pdf_url = Column(Text, nullable=True)
    mp3_url = Column(Text, nullable=True)
    passing_score = Column(DECIMAL(5, 2), nullable=True)
    max_score = Column(DECIMAL(5, 2), nullable=True)
    version = Column(Integer, default=1)
    is_sample = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True, nullable=False)
    attempt_limit = Column(Integer, default=1)
    created_by = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    sections = relationship("ExamSection", back_populates="exam", cascade="all, delete-orphan")
    attempts = relationship("ExamAttempt", back_populates="exam", cascade="all, delete-orphan")


class ExamSection(Base):
    __tablename__ = "exam_sections"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    exam_id = Column(BigInteger, ForeignKey("exams.id", ondelete="CASCADE"), nullable=False)
    section_type = Column(String(20), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    duration_minutes = Column(Integer, default=0)
    order_index = Column(Integer, default=0)
    instructions = Column(Text, nullable=True)
    total_questions = Column(Integer, default=0)
    max_score = Column(DECIMAL(5, 2), nullable=True)
    passing_score = Column(DECIMAL(5, 2), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    exam = relationship("Exam", back_populates="sections")
    questions = relationship("ExamQuestion", back_populates="section", cascade="all, delete-orphan")


class ExamQuestion(Base):
    __tablename__ = "exam_questions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    section_id = Column(BigInteger, ForeignKey("exam_sections.id", ondelete="CASCADE"), nullable=False)
    question_number = Column(Integer, default=0)
    question_type = Column(String(50), default="multiple_choice")
    question_text = Column(Text, nullable=False)
    options = Column(JSONB, nullable=True)
    correct_answer = Column(Text, nullable=False)
    explanation = Column(Text, nullable=True)
    points = Column(DECIMAL(5, 2), default=1.00)
    difficulty = Column(String(20), default="medium")
    audio_url = Column(Text, nullable=True)
    image_url = Column(Text, nullable=True)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    section = relationship("ExamSection", back_populates="questions")


class ExamAttempt(Base):
    __tablename__ = "exam_attempts"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    exam_id = Column(BigInteger, ForeignKey("exams.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    attempt_number = Column(Integer, default=1)
    status = Column(String(20), default="in_progress")
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    reading_score = Column(DECIMAL(5, 2), nullable=True)
    listening_score = Column(DECIMAL(5, 2), nullable=True)
    speaking_score = Column(DECIMAL(5, 2), nullable=True)
    writing_score = Column(DECIMAL(5, 2), nullable=True)
    speaking_feedback = Column(Text, nullable=True)
    writing_feedback = Column(Text, nullable=True)
    total_score = Column(DECIMAL(5, 2), nullable=True)
    cefr_result = Column(String(10), nullable=True)
    passed = Column(Boolean, nullable=True)
    confidence_score = Column(DECIMAL(5, 2), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    exam = relationship("Exam", back_populates="attempts")
    answers = relationship("ExamAnswer", back_populates="attempt", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("exam_id", "user_id", "attempt_number"),
    )


class ExamAnswer(Base):
    __tablename__ = "exam_answers"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    attempt_id = Column(BigInteger, ForeignKey("exam_attempts.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(BigInteger, ForeignKey("exam_questions.id", ondelete="CASCADE"), nullable=False)
    user_answer = Column(Text, nullable=True)
    is_correct = Column(Boolean, nullable=True)
    score = Column(DECIMAL(5, 2), nullable=True)
    ai_feedback = Column(Text, nullable=True)
    answered_at = Column(DateTime(timezone=True), server_default=func.now())

    attempt = relationship("ExamAttempt", back_populates="answers")