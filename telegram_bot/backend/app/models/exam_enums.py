import enum

class ExamType(str, enum.Enum):
    FULL = "full"
    LISTENING = "listening"
    READING = "reading"
    WRITING = "writing"
    SPEAKING = "speaking"

class CEFRLevel(str, enum.Enum):
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"

class ItemType(str, enum.Enum):
    LISTENING_QUESTION = "listening_question"
    READING_QUESTION = "reading_question"
    WRITING_TASK = "writing_task"
    SPEAKING_TASK = "speaking_task"

class AttemptStatus(str, enum.Enum):
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    SCORING = "scoring"
    COMPLETED = "completed"
    NEEDS_REVIEW = "needs_review"
    FAILED = "failed"

class BlockAttemptStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"

class AIAnswerStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"
    NEEDS_REVIEW = "needs_review"

class AIJobType(str, enum.Enum):
    TRANSCRIBE = "transcribe"
    EVALUATE_WRITING = "evaluate_writing"
    EVALUATE_SPEAKING = "evaluate_speaking"

class AIJobStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"

class MediaType(str, enum.Enum):
    AUDIO = "audio"
    IMAGE = "image"
    DOCUMENT = "document"