"""
cleanup_service.py
DB va storage'ni avtomatik tozalash servisi
"""
import os
import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

RETENTION = {
    "api_logs": 30,
    "error_logs": 90,
    "audit_logs": 365,
    "ai_jobs_payload": 14,
    "ai_jobs_rows": 90,
    "speaking_audio": 30,
    "broadcast_history": 90,
}

MEDIA_ROOT = os.getenv("MEDIA_ROOT", "/app/media")


def _delete_older_than(db: Session, table: str, days: int) -> int:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    result = db.execute(
        text(f"DELETE FROM {table} WHERE created_at < :cutoff"),
        {"cutoff": cutoff},
    )
    db.commit()
    return result.rowcount or 0


def purge_old_logs(db: Session) -> dict:
    stats = {}
    for table, days in [
        ("api_logs", RETENTION["api_logs"]),
        ("error_logs", RETENTION["error_logs"]),
        ("audit_logs", RETENTION["audit_logs"]),
    ]:
        try:
            stats[table] = _delete_older_than(db, table, days)
        except Exception as e:
            logger.warning("%s tozalashda xato: %s", table, e)
            db.rollback()
            stats[table] = 0
    return stats


def purge_ai_job_payloads(db: Session) -> int:
    cutoff = datetime.now(timezone.utc) - timedelta(days=RETENTION["ai_jobs_payload"])
    result = db.execute(
        text("""
            UPDATE exam_ai_jobs
            SET request_payload = NULL, response_payload = NULL
            WHERE status IN ('completed', 'error')
              AND updated_at < :cutoff
              AND request_payload IS NOT NULL
        """),
        {"cutoff": cutoff},
    )
    db.commit()
    return result.rowcount or 0


def purge_speaking_audio(db: Session) -> int:
    cutoff = datetime.now(timezone.utc) - timedelta(days=RETENTION["speaking_audio"])
    rows = db.execute(
        text("""
            SELECT a.id, a.audio_url
            FROM exam_answers a
            JOIN exam_attempts at ON at.id = a.attempt_id
            WHERE a.audio_url IS NOT NULL
              AND a.ai_status = 'completed'
              AND at.completed_at IS NOT NULL
              AND at.completed_at < :cutoff
        """),
        {"cutoff": cutoff},
    ).fetchall()

    deleted = 0
    for row in rows:
        try:
            if row.audio_url:
                file_path = os.path.join(MEDIA_ROOT, row.audio_url.replace("/media/", ""))
                if os.path.exists(file_path):
                    os.remove(file_path)
                    deleted += 1
        except Exception as e:
            logger.warning("Audio o'chirilmadi: %s", e)

    if rows:
        ids = [r.id for r in rows]
        db.execute(
            text("UPDATE exam_answers SET audio_url = NULL WHERE id = ANY(:ids)"),
            {"ids": ids},
        )
        db.commit()
    return deleted


def run_full_cleanup(db: Session) -> dict:
    logger.info("🧹 Cleanup boshlandi...")
    report = {
        "logs": purge_old_logs(db),
        "ai_payloads": purge_ai_job_payloads(db),
        "speaking_audio": purge_speaking_audio(db),
    }
    logger.info("🧹 Cleanup yakunlandi: %s", report)
    return report