from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import bcrypt


def hash_password(password: str) -> str:
    """Hash password using bcrypt (rounds: 12)."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode(), salt).decode()


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except (ValueError, TypeError):
        return False