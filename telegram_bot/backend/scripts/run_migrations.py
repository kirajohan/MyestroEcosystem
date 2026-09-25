"""
run_migrations.py

Idempotent migration runner:
- Agar jadvallar allaqachon mavjud bo'lsa (Postgres entrypoint yaratgan)
  init.sql o'tkazib yuboriladi va versiya belgilanadi.
- Aks holda init.sql + versions/ ketma-ket qo'llanadi.
"""
import os
import glob
import logging
import psycopg2

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

MIGRATIONS_DIR = "/app/migrations"
MASTER_VERSION = "000_master_init.sql"

DATABASE_URL = os.environ.get("DATABASE_URL", "")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL topilmadi!")

if "sslmode" not in DATABASE_URL and ("rlwy.net" in DATABASE_URL or "railway" in DATABASE_URL):
    sep = "&" if "?" in DATABASE_URL else "?"
    DATABASE_URL = f"{DATABASE_URL}{sep}sslmode=require"


def table_exists(cur, table: str) -> bool:
    """Jadval mavjudligini tekshirish."""
    cur.execute(
        "SELECT 1 FROM information_schema.tables "
        "WHERE table_schema = 'public' AND table_name = %s",
        (table,),
    )
    return cur.fetchone() is not None


def run_sql_file(cur, path: str):
    with open(path, "r", encoding="utf-8") as f:
        sql = f.read()
    if sql.strip():
        cur.execute(sql)


def main():
    logger.info("Connecting to PostgreSQL...")
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = False

    try:
        cur = conn.cursor()

        # Tracking jadvali
        cur.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version TEXT PRIMARY KEY,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
        """)
        conn.commit()

        cur.execute("SELECT version FROM schema_migrations")
        applied = {row[0] for row in cur.fetchall()}

        # ─── 1. Master init.sql ───
        if MASTER_VERSION not in applied:
            if table_exists(cur, "users"):
                # Jadvallar Postgres entrypoint (01_init.sql) tomonidan yaratilgan
                logger.info("Tables already exist (created by Postgres init) — skipping init.sql")
                cur.execute(
                    "INSERT INTO schema_migrations (version) VALUES (%s) ON CONFLICT DO NOTHING",
                    (MASTER_VERSION,),
                )
                conn.commit()
            else:
                logger.info("Applying init.sql (all tables)...")
                try:
                    run_sql_file(cur, os.path.join(MIGRATIONS_DIR, "init.sql"))
                    cur.execute(
                        "INSERT INTO schema_migrations (version) VALUES (%s) ON CONFLICT DO NOTHING",
                        (MASTER_VERSION,),
                    )
                    conn.commit()
                    logger.info("init.sql completed")
                except Exception as e:
                    conn.rollback()
                    logger.error(f"init.sql failed: {e}")
                    raise
        else:
            logger.info("Master init already applied")

        # ─── 2. versions/ ketma-ket ───
        for path in sorted(glob.glob(os.path.join(MIGRATIONS_DIR, "versions", "*.sql"))):
            version = os.path.basename(path)
            if version in applied:
                logger.info(f"Skip {version}")
                continue
            logger.info(f"Applying {version}...")
            try:
                run_sql_file(cur, path)
                cur.execute(
                    "INSERT INTO schema_migrations (version) VALUES (%s) ON CONFLICT DO NOTHING",
                    (version,),
                )
                conn.commit()
                logger.info(f"{version} completed")
            except Exception as e:
                conn.rollback()
                logger.error(f"{version} failed: {e}")
                raise

        logger.info("All migrations completed!")

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()