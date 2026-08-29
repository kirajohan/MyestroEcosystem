"""Models package — SQLAlchemy models registry."""

from app.database import Base

# Core models
from .user import User, Session
from .conversation import ConversationThread, Message
from .knowledge import KnowledgeCategory, KnowledgeDoc
from .logs import ApiLog, ErrorLog, AuditLog
from .settings import SystemSetting
from .content import ContentItem
from .bot_text import BotText
from .admin_message import AdminMessage
from .broadcast import BroadcastJob, BroadcastHistory

# AI Memory
try:
    from .ai_memory import AIMemorySession
except Exception:
    AIMemorySession = None

# INBOX
try:
    from .inbox import InboxMessage, InboxMessageHistory
except Exception:
    InboxMessage = InboxMessageHistory = None

# TESTS
try:
    from .tests import Test, TestQuestion, TestAttempt
except Exception:
    Test = TestQuestion = TestAttempt = None

# EXAM (YANGI SXEMA)
try:
    from .exam import (
        Exam, ExamBlock, ExamItem, ExamOption, ExamRubric,
        ExamAttempt, ExamAttemptBlock, ExamAnswer, ExamAIJob, ExamMedia
    )
except Exception as e:
    print(f"⚠️ Exam modellarni import qilishda xatolik: {e}")
    Exam = ExamBlock = ExamItem = ExamOption = ExamRubric = None
    ExamAttempt = ExamAttemptBlock = ExamAnswer = ExamAIJob = ExamMedia = None

__all__ = [
    "Base", "User", "Session", "ConversationThread", "Message",
    "KnowledgeCategory", "KnowledgeDoc", "ApiLog", "ErrorLog", "AuditLog",
    "SystemSetting", "ContentItem", "BotText", "AdminMessage",
    "BroadcastJob", "BroadcastHistory", "InboxMessage", "InboxMessageHistory",
    "AIMemorySession", "Test", "TestQuestion", "TestAttempt",
    # Yangi Exam modellar
    "Exam", "ExamBlock", "ExamItem", "ExamOption", "ExamRubric",
    "ExamAttempt", "ExamAttemptBlock", "ExamAnswer", "ExamAIJob", "ExamMedia"
]