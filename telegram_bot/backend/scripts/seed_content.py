"""Seed default content (Video / File lessons) for testing."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models.content import ContentItem


def seed_content():
    """Create default video and file lessons."""
    engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # Check if content already exists
        existing = db.query(ContentItem).first()
        if existing:
            print("Content already seeded. Skipping.")
            return

        default_content = [
            ContentItem(
                title="1. English Grammar Basics",
                description="Ingliz tili grammatikasi asoslari. A1 daraja uchun.",
                content_type="video",
                file_path="/app/content/lesson1_grammar.mp4",
                telegram_file_id="",
                is_active=True,
            ),
            ContentItem(
                title="2. To Be Fe'li",
                description="To be fe'li: am, is, are. A1 daraja uchun.",
                content_type="video",
                file_path="/app/content/lesson2_to_be.mp4",
                telegram_file_id="",
                is_active=True,
            ),
            ContentItem(
                title="3. Present Simple",
                description="Present Simple zamon. A1 daraja uchun.",
                content_type="video",
                file_path="/app/content/lesson3_present_simple.mp4",
                telegram_file_id="",
                is_active=True,
            ),
            ContentItem(
                title="1. Grammar Book (PDF)",
                description="Ingliz tili grammatikasi kitobi. PDF format.",
                content_type="file",
                file_path="/app/content/grammar_book.pdf",
                telegram_file_id="",
                is_active=True,
            ),
            ContentItem(
                title="2. Verb Conjugation Guide",
                description="Fe'llar conjugatsiyasi qo'llanmasi.",
                content_type="file",
                file_path="/app/content/verb_guide.pdf",
                telegram_file_id="",
                is_active=True,
            ),
            ContentItem(
                title="Welcome Message",
                description="Botga xush kelibsiz xabari.",
                content_type="text",
                file_path="",
                telegram_file_id="",
                is_active=True,
            ),
        ]

        for item in default_content:
            db.add(item)

        db.commit()
        print("=" * 50)
        print("DEFAULT CONTENT SEEDED SUCCESSFULLY")
        print("=" * 50)
        print(f"Items: {len(default_content)}")
        print("=" * 50)

    except Exception as e:
        print(f"ERROR: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_content()
