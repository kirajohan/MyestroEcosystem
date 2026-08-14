from typing import List, Optional, Callable
from fastapi import Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session as DBSession
from app.database import get_db
from app.models.user import User
from app.models.logs import ApiLog
from app.core.security import verify_token
from app.core.exceptions import UnauthorizedException, ForbiddenException
from app.config import settings
import time

security = HTTPBearer(auto_error=False)

from fastapi import Depends
import redis.asyncio as redis
from app.config import settings

_redis_client = None

async def get_redis():
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    return _redis_client

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: DBSession = Depends(get_db),
) -> User:
    """Validate JWT and return current user."""
    if credentials is None:
        raise UnauthorizedException("Not authenticated")

    try:
        payload = verify_token(credentials.credentials, settings.JWT_ACCESS_SECRET)
        user_id = int(payload.get("sub", 0))
    except ValueError:
        raise UnauthorizedException("Invalid or expired token")

    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise UnauthorizedException("User not found or inactive")

    return user


def require_role(roles: List[str]) -> Callable:
    """Dependency factory — requires specific roles."""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise ForbiddenException(f"Requires one of roles: {roles}")
        return current_user
    return role_checker


def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Require admin or superadmin role."""
    if current_user.role not in ("admin", "superadmin"):
        raise ForbiddenException("Requires admin role")
    return current_user


def get_superadmin_user(current_user: User = Depends(get_current_user)) -> User:
    """Require superadmin role."""
    if current_user.role != "superadmin":
        raise ForbiddenException("Requires superadmin role")
    return current_user


def log_api_request(request: Request, db: DBSession, user_id: Optional[int] = None):
    """Log API request to api_logs table."""
    start_time = time.time()

    def _log(response_body: Optional[str] = None):
        elapsed = int((time.time() - start_time) * 1000)
        body = None
        # FastAPI sync endpoints don't have await, so skip body for sync logging
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


require_admin = require_role(["admin", "superadmin"])
require_superadmin = require_role(["superadmin"])