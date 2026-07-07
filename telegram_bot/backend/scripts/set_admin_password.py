#!/usr/bin/env python3
"""Set admin password script."""
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config import settings
from app.database import SessionLocal
from app.models.user import User
from app.core.security import hash_password

db = SessionLocal()

try:
    user = db.query(User).filter(User.email == "admin@example.com").first()
    if not user:
        print("User not found")
        sys.exit(1)
    
    hashed = hash_password("password123")
    user.password_hash = hashed
    db.commit()
    
    print(f"Password set successfully for admin@example.com")
    print(f"Hashed: {hashed}")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
finally:
    db.close()
