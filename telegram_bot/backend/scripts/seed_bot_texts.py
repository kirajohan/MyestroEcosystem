"""Seed ALL bot texts from TRANSLATIONS dict to database."""

import sys
import os

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "bot"))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models.bot_text import BotText
from bot.utils.i18n import TRANSLATIONS


def seed_all_bot_texts():
    """Create ALL bot texts from TRANSLATIONS dict for all languages."""
    engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # Count existing
        existing_count = db.query(BotText).count()
        print(f"Hozirda DB da {existing_count} ta matn bor")

        # Prepare all texts from TRANSLATIONS
        texts_to_upsert = []
        
        for lang, translations in TRANSLATIONS.items():
            for key, text in translations.items():
                texts_to_upsert.append({
                    "key": key,
                    "lang": lang,
                    "text": text
                })

        print(f"TRANSLATIONS dict dan {len(texts_to_upsert)} ta matn topildi")

        # Bulk upsert
        created = 0
        updated = 0
        
        for text_data in texts_to_upsert:
            existing = db.query(BotText).filter(
                BotText.key == text_data["key"],
                BotText.lang == text_data["lang"],
            ).first()
            
            if existing:
                if existing.text != text_data["text"]:
                    existing.text = text_data["text"]
                    updated += 1
            else:
                entry = BotText(**text_data)
                db.add(entry)
                created += 1

        db.commit()
        
        print("=" * 50)
        print("BOT TEXTS SEEDED SUCCESSFULLY")
        print("=" * 50)
        print(f"Created: {created}")
        print(f"Updated: {updated}")
        print(f"Total: {created + updated}")
        print("=" * 50)

    except Exception as e:
        print(f"ERROR: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_all_bot_texts()