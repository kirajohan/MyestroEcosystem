"""JSON Logging Formatter — Format logs as structured JSON for easy parsing.

Usage:
    import logging
    from bot.utils.json_logger import setup_json_logging
    
    setup_json_logging()
    logger = logging.getLogger(__name__)
    logger.info("User logged in", extra={"user_id": 123})
"""

import json
import logging
import traceback
import sys
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """Format log records as JSON for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Convert log record to JSON string."""
        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_obj["exception"] = traceback.format_exception(
                *record.exc_info
            ).__str__()
        elif record.exc_text:
            log_obj["exception"] = record.exc_text

        # Add extra fields
        if hasattr(record, "user_id"):
            log_obj["user_id"] = record.user_id
        if hasattr(record, "extra_data"):
            log_obj["extra_data"] = record.extra_data

        return json.dumps(log_obj, ensure_ascii=False)


def setup_json_logging(level=logging.INFO):
    """Configure root logger to output JSON format."""
    # Remove existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create console handler with JSON formatter
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())

    root_logger.addHandler(handler)
    root_logger.setLevel(level)

    return root_logger


def get_logger(name: str) -> logging.LoggerAdapter:
    """Get logger with optional extra fields support."""
    logger = logging.getLogger(name)

    class LoggerAdapter(logging.LoggerAdapter):
        def process(self, msg, kwargs):
            return msg, kwargs

    return LoggerAdapter(logger, {})


# Export for easy import
__all__ = ["JSONFormatter", "setup_json_logging", "get_logger"]
