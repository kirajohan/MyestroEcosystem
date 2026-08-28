import os
import pathlib
from dotenv import load_dotenv  # <-- YANGI QO'SHILDI

# .env faylni avtomatik yuklash
load_dotenv()                 # <-- YANGI QO'SHILDI

import psycopg2
from psycopg2 import sql

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5433/myestro"
)
# ... qolgan kod o'zgarishsiz ...

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
MIGRATIONS_DIR = BASE_DIR / "migrations" / "versions"


def ensure_schema_migrations(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY,
            applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
    """)


def get_applied_versions(cur):
    cur.execute("SELECT version FROM schema_migrations;")
    return {row[0] for row in cur.fetchall()}


def apply_migration(conn, cur, file: pathlib.Path):
    version = file.stem
    script = file.read_text(encoding="utf-8")

    print(f"Applying migration: {version}")

    cur.execute(sql.SQL(script))
    cur.execute(
        "INSERT INTO schema_migrations (version) VALUES (%s);",
        (version,)
    )

    conn.commit()
    print(f"Applied: {version}")


def main():
    if not MIGRATIONS_DIR.exists():
        print(f"Migrations folder not found: {MIGRATIONS_DIR}")
        return

    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = False

    try:
        cur = conn.cursor()

        ensure_schema_migrations(cur)
        conn.commit()

        applied = get_applied_versions(cur)

        migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))

        if not migration_files:
            print("No SQL migration files found.")
            return

        for file in migration_files:
            version = file.stem

            if version in applied:
                print(f"Skipping already applied: {version}")
                continue

            try:
                apply_migration(conn, cur, file)
            except Exception as error:
                conn.rollback()
                print(f"Migration failed: {version}")
                print(error)
                raise

    finally:
        conn.close()


if __name__ == "__main__":
    main()