from sqlalchemy import Column, BigInteger, String, Text, Integer, Float, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base
from .exam_enums import (
    ExamType, CEFRLevel, ItemType, AttemptStatus, 
    BlockAttemptStatus, AIAnswerStatus, AIJobType, 
    AIJobStatus, MediaType
)

class Exam(Base):
    __tablename__ = "exams"
    __table_args__ = {"extend_existing": True}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    code = Column(String, unique=True, nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    exam_type = Column(Enum(ExamType), nullable=False)
    cefr_level = Column(Enum(CEFRLevel), nullable=True)
    time_limit_sec = Column(Integer, nullable=False)
    is_published = Column(Boolean, default=False, nullable=False)
    scoring_config = Column(JSONB, nullable=True) # Masalan: {"weights": {"L": 25, "R": 25, "W": 25, "S": 25}}
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    blocks = relationship("ExamBlock", back_populates="exam", cascade="all, delete-orphan")
    attempts = relationship("ExamAttempt", back_populates="exam")


class ExamBlock(Base):
    __tablename__ = "exam_blocks"
    __table_args__ = {"extend_existing": True}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    exam_id = Column(BigInteger, ForeignKey("exams.id", ondelete="CASCADE"), nullable=False)
    block_type = Column(Enum(ExamType), nullable=False) # listening, reading, writing, speaking
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    instructions = Column(Text, nullable=True)
    order = Column(Integer, nullable=False)
    time_limit_sec = Column(Integer, nullable=False)
    config = Column(JSONB, nullable=True) # Masalan: {"max_listens": 2}
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    exam = relationship("Exam", back_populates="blocks")
    items = relationship("ExamItem", back_populates="block", cascade="all, delete-orphan")
    attempt_blocks = relationship("ExamAttemptBlock", back_populates="block")


class ExamRubric(Base):
    __tablename__ = "exam_rubrics"
    __table_args__ = {"extend_existing": True}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    code = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    skill_type = Column(Enum(ExamType), nullable=False) # writing or speaking
    system_prompt = Column(Text, nullable=False)
    user_prompt_template = Column(Text, nullable=False)
    scoring_schema = Column(JSONB, nullable=False) # AI qaytarishi kerak bo'lgan JSON strukturasi
    cefr_mapping = Column(JSONB, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    items = relationship("ExamItem", back_populates="rubric")


class ExamItem(Base):
    __tablename__ = "exam_items"
    __table_args__ = {"extend_existing": True}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    block_id = Column(BigInteger, ForeignKey("exam_blocks.id", ondelete="CASCADE"), nullable=False)
    item_type = Column(Enum(ItemType), nullable=False)
    title = Column(String, nullable=True)
    instruction = Column(Text, nullable=True)
    question_text = Column(Text, nullable=True)
    passage_text = Column(Text, nullable=True) # Reading uchun matn
    audio_url = Column(String, nullable=True)
    audio_duration_sec = Column(Integer, nullable=True)
    transcript_text = Column(Text, nullable=True) # Listening/Speaking uchun etalon transkript
    min_words = Column(Integer, nullable=True) # Writing uchun
    max_words = Column(Integer, nullable=True) # Writing uchun
    preparation_time_sec = Column(Integer, nullable=True) # Speaking uchun
    answer_time_sec = Column(Integer, nullable=True) # Speaking uchun
    max_score = Column(Float, nullable=False, default=1.0)
    order = Column(Integer, nullable=False)
    config = Column(JSONB, nullable=True)
    answer_key = Column(JSONB, nullable=True) # Avtomatik tekshirish uchun to'g'ri javoblar
    rubric_id = Column(BigInteger, ForeignKey("exam_rubrics.id", ondelete="SET NULL"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    block = relationship("ExamBlock", back_populates="items")
    rubric = relationship("ExamRubric", back_populates="items")
    options = relationship("ExamOption", back_populates="item", cascade="all, delete-orphan")
    answers = relationship("ExamAnswer", back_populates="item")


class ExamOption(Base):
    __tablename__ = "exam_options"
    __table_args__ = {"extend_existing": True}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    item_id = Column(BigInteger, ForeignKey("exam_items.id", ondelete="CASCADE"), nullable=False)
    text = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False, nullable=False)
    order = Column(Integer, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    item = relationship("ExamItem", back_populates="options")


class ExamAttempt(Base):
    __tablename__ = "exam_attempts"
    __table_args__ = {"extend_existing": True}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    exam_id = Column(BigInteger, ForeignKey("exams.id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum(AttemptStatus), default=AttemptStatus.CREATED, nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    deadline = Column(DateTime(timezone=True), nullable=True) # Server taymeri uchun
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    total_score = Column(Float, nullable=True)
    cefr_estimate = Column(String, nullable=True)
    meta_data = Column(JSONB, nullable=True)  # Changed from 'metadata' to 'meta_data'
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    exam = relationship("Exam", back_populates="attempts")
    attempt_blocks = relationship("ExamAttemptBlock", back_populates="attempt", cascade="all, delete-orphan")
    answers = relationship("ExamAnswer", back_populates="attempt", cascade="all, delete-orphan")
    ai_jobs = relationship("ExamAIJob", back_populates="attempt", cascade="all, delete-orphan")


class ExamAttemptBlock(Base):
    __tablename__ = "exam_attempt_blocks"
    __table_args__ = {"extend_existing": True}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    attempt_id = Column(BigInteger, ForeignKey("exam_attempts.id", ondelete="CASCADE"), nullable=False)
    block_id = Column(BigInteger, ForeignKey("exam_blocks.id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum(BlockAttemptStatus), default=BlockAttemptStatus.PENDING, nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    score = Column(Float, nullable=True)
    meta_data = Column(JSONB, nullable=True)  # Changed from 'metadata'

    # Relationships
    attempt = relationship("ExamAttempt", back_populates="attempt_blocks")
    block = relationship("ExamBlock", back_populates="attempt_blocks")


class ExamAnswer(Base):
    __tablename__ = "exam_answers"
    __table_args__ = {"extend_existing": True}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    attempt_id = Column(BigInteger, ForeignKey("exam_attempts.id", ondelete="CASCADE"), nullable=False)
    item_id = Column(BigInteger, ForeignKey("exam_items.id", ondelete="CASCADE"), nullable=False)
    selected_options = Column(JSONB, nullable=True) # Tanlangan variantlar ID lari [1, 3]
    text_answer = Column(Text, nullable=True)
    audio_url = Column(String, nullable=True)
    transcript_text = Column(Text, nullable=True)
    auto_score = Column(Float, nullable=True)
    ai_score = Column(Float, nullable=True)
    final_score = Column(Float, nullable=True)
    ai_status = Column(Enum(AIAnswerStatus), default=AIAnswerStatus.PENDING, nullable=True)
    feedback = Column(JSONB, nullable=True) # AI dan kelgan tahlil
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    attempt = relationship("ExamAttempt", back_populates="answers")
    item = relationship("ExamItem", back_populates="answers")


class ExamAIJob(Base):
    __tablename__ = "exam_ai_jobs"
    __table_args__ = {"extend_existing": True}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    attempt_id = Column(BigInteger, ForeignKey("exam_attempts.id", ondelete="CASCADE"), nullable=False)
    answer_id = Column(BigInteger, ForeignKey("exam_answers.id", ondelete="SET NULL"), nullable=True)
    job_type = Column(Enum(AIJobType), nullable=False)
    status = Column(Enum(AIJobStatus), default=AIJobStatus.PENDING, nullable=False)
    provider = Column(String, nullable=True) # 'openai-whisper', 'openrouter-gpt4'
    request_payload = Column(JSONB, nullable=True)
    response_payload = Column(JSONB, nullable=True)
    error_message = Column(Text, nullable=True)
    attempts_count = Column(Integer, default=0, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    attempt = relationship("ExamAttempt", back_populates="ai_jobs")


class ExamMedia(Base):
    __tablename__ = "exam_media"
    __table_args__ = {"extend_existing": True}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    owner_type = Column(String, nullable=False) # 'exam_item', 'exam_answer'
    owner_id = Column(BigInteger, nullable=False)
    file_type = Column(Enum(MediaType), nullable=False)
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    mime_type = Column(String, nullable=False)
    size_bytes = Column(BigInteger, nullable=False)
    duration_sec = Column(Integer, nullable=True)
    transcript_text = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
