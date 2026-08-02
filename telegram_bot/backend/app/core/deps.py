from typing import Optional, Callable
from fastapi import Depends, Request
from sqlalchemy.orm import Session as DBSession
from app.database import get_db
from app.models.logs import ApiLog
from app.config import settings
import time


def log_api_request(request: Request, db: DBSession, user_id: Optional[int] = None):
    """Log API request to api_logs table."""
    start_time = time.time()

    def _log(response_body: Optional[str] = None):
        elapsed = int((time.time() - start_time) * 1000)
        body = None
        log_entry = ApiLog(
            user_id=user_id,
            endpoint=str(request.url.path),
            method=request.method,
            status_code=200,
            response_time_ms=elapsed,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            request_body=body,
        )
        db.add(log_entry)
        db.commit()

    return _log