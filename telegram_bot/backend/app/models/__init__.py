"""Models package — SQLAlchemy models registry.

Import model classes here so importing this package registers them
with the SQLAlchemy `Base` metadata. Avoid runtime prints or other
side-effects so imports remain safe in different contexts.
"""

# Base (must be imported before models)
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

# AI Memory model
try:
    from .ai_memory import AIMemorySession
except Exception:
    AIMemorySession = None

# Optional models — guard imports to avoid ImportError during partial setups
try:
    from .exam import Exam, ExamSection, ExamQuestion, ExamAttempt, ExamAnswer
except Exception:
    Exam = ExamSection = ExamQuestion = ExamAttempt = ExamAnswer = None

try:
    from .inbox import InboxMessage, InboxMessageHistory
except Exception:
    InboxMessage = InboxMessageHistory = None

try:
    from .tests import Test, TestQuestion, TestAttempt
except Exception:
    Test = TestQuestion = TestAttempt = None

__all__ = [
    "Base",
    "User",
    "Session",
    "ConversationThread",
    "Message",
    "KnowledgeCategory",
    "KnowledgeDoc",
    "ApiLog",
    "ErrorLog",
    "AuditLog",
    "SystemSetting",
    "ContentItem",
    "BotText",
    "AdminMessage",
    "BroadcastJob",
    "BroadcastHistory",
    "InboxMessage",
    "InboxMessageHistory",
    "AIMemorySession",
    "Exam",
    "ExamSection",
    "ExamQuestion",
    "ExamAttempt",
    "ExamAnswer",
    "Test",
    "TestQuestion",
    "TestAttempt",
]
