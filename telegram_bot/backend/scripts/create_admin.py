"""Create admin user script — run inside the backend Docker container.

Usage (after docker compose up):
    docker compose exec backend python /app/scripts/create_admin.py

Or locally if you have the Python environment set up:
    cd telegram_bot/backend
    python scripts/create_admin.py
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models.user import User
from app.core.security import hash_password


def create_admin_user():
    """Create a default admin/superadmin user."""
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # Check if admin already exists
        existing = db.query(User).filter(User.email == "admin@myestro.com").first()
        if existing:
            print(f"Admin user already exists: {existing.email} (role: {existing.role})")
            print(f"Password: admin123")
            return

        # Create admin user with bcrypt hashed password
        admin = User(
            email="admin@myestro.com",
            password_hash=hash_password("admin123"),
            full_name="Super Admin",
            role="admin",
            cefr_level="C2",
            target_level="C2",
            lang="uz",
            auth_provider="email",
            is_active=True,
            is_verified=True,
            profile_completed=True,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

        print("=" * 50)
        print("ADMIN USER CREATED SUCCESSFULLY")
        print("=" * 50)
        print(f"Email:    admin@myestro.com")
        print(f"Password: admin123")
        print(f"Role:     admin")
        print(f"Name:     Super Admin")
        print("=" * 50)
        print("Login at: http://localhost:3002")
        print("=" * 50)

    except Exception as e:
        print(f"ERROR: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_admin_user()
