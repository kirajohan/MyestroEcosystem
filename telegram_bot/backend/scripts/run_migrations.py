"""
run_migrations.py

Railway PostgreSQL uchun idempotent migration runner.
Har bir deploy'da avtomatik ishlaydi.

Strategiya:
1. schema_migrations jadvali yaratiladi
2. Agar '000_master_init.sql' qo'llanmagan bo'lsa → init.sql bajariladi
3. Keyin versions/ papkasidagi yangi migrationlar qo'llanadi

Railway uchun SSL avtomatik qo'shiladi (agar public URL bo'lsa).
"""
import os
import glob
import logging
import psycopg2

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL", "")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable topilmadi!")

# Railway public URL bo'lsa SSL qo'shish
if "sslmode" not in DATABASE_URL and ("rlwy.net" in DATABASE_URL or "railway" in DATABASE_URL):
    sep = "&" if "?" in DATABASE_URL else "?"
    DATABASE_URL = f"{DATABASE_URL}{sep}sslmode=require"
    logger.info("🔒 SSL mode enabled (Railway public URL detected)")
else:
    logger.info("🔓 SSL mode disabled (private network or local)")


def ensure_schema_migrations(cur):
    """schema_migrations tracking jadvalini yaratish."""
    cur.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY,
            applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)


def get_applied(cur) -> set:
    """Allaqachon qo'llangan migration'larni olish."""
    cur.execute("SELECT version FROM schema_migrations")
    return {row[0] for row in cur.fetchall()}


def run_sql_file(cur, path: str):
    """SQL faylni o'qib, bajaradi."""
    with open(path, "r", encoding="utf-8") as f:
        sql = f.read()
    if sql.strip():
        cur.execute(sql)


def main():
    logger.info("🔌 Railway PostgreSQL'ga ulanmoqda...")
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = False
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        raise

    try:
        cur = conn.cursor()

        # 1. schema_migrations tracking
        logger.info("📋 Checking schema_migrations table...")
        ensure_schema_migrations(cur)
        conn.commit()
        applied = get_applied(cur)
        logger.info(f"✅ Found {len(applied)} applied migrations")

        # 2. Master init.sql
        if "000_master_init.sql" not in applied:
            logger.info("▶️  Applying master init.sql (all tables)...")
            try:
                run_sql_file(cur, "migrations/init.sql")
                cur.execute(
                    "INSERT INTO schema_migrations (version) VALUES (%s) ON CONFLICT DO NOTHING",
                    ("000_master_init.sql",),
                )
                conn.commit()
                logger.info("✅ Master init completed")
            except Exception as e:
                conn.rollback()
                logger.error(f"❌ init.sql failed: {e}")
                raise
        else:
            logger.info("⏭️  Master init already applied")

        # 3. versions/ papkasidan qo'shimcha migrationlar
        version_files = sorted(glob.glob("migrations/versions/*.sql"))
        if version_files:
            logger.info(f"📂 Found {len(version_files)} version files")
            applied = get_applied(cur)
            
            for path in version_files:
                version = os.path.basename(path)
                if version in applied:
                    logger.info(f"⏭️  Skip {version} (already applied)")
                    continue
                
                logger.info(f"▶️  Applying {version}...")
                try:
                    run_sql_file(cur, path)
                    cur.execute(
                        "INSERT INTO schema_migrations (version) VALUES (%s) ON CONFLICT DO NOTHING",
                        (version,),
                    )
                    conn.commit()
                    logger.info(f"✅ {version} completed")
                except Exception as e:
                    conn.rollback()
                    logger.error(f"❌ {version} failed: {e}")
                    raise
        else:
            logger.info("📂 No additional version files found")

        logger.info("🎉 All migrations completed successfully!")

    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()