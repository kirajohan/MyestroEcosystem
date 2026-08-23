#!/usr/bin/env python
"""Run SQL migrations from the migrations directory.

This script runs all SQL migration files in order against the PostgreSQL
database specified by DATABASE_URL. All migrations use CREATE TABLE IF NOT
EXISTS, so they are safe to run repeatedly (idempotent).
"""

import os
import sys
import psycopg2
from pathlib import Path
from urllib.parse import urlparse

# Migration files in dependency order (init.sql MUST be first — creates users table)
MIGRATION_FILES = [
    "init.sql",
    "broadcast_tables.sql",
    "inbox_tables.sql",
    "exam_tables.sql",
    "tests_tables.sql",
    "global_settings.sql",
    "logs_table.sql",
    "admin_messages.sql",
]


def run_migrations():
    """Run SQL migration files in order."""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("ERROR: DATABASE_URL not set")
        return False

    # Migrations directory is at /app/migrations in the container
    migrations_dir = Path(__file__).parent.parent / "migrations"

    if not migrations_dir.exists():
        print(f"Migrations directory not found: {migrations_dir}")
        return False

    # Parse connection string
    try:
        parsed = urlparse(db_url)
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            user=parsed.username,
            password=parsed.password,
            dbname=parsed.path.lstrip('/'),
        )
        cur = conn.cursor()

        for migration_file in MIGRATION_FILES:
            filepath = migrations_dir / migration_file
            if not filepath.exists():
                print(f"⊘ Skipping {migration_file} (not found)")
                continue

            print(f"→ Running {migration_file}...", end=" ")
            try:
                with open(filepath, 'r') as f:
                    sql = f.read()
                cur.execute(sql)
                conn.commit()
                print("✓")
            except Exception as e:
                print(f"✗ {e}")
                conn.rollback()
                return False

        cur.close()
        conn.close()
        print("\n✓ All migrations completed successfully")
        return True

    except Exception as e:
        print(f"ERROR: {e}")
        return False


if __name__ == "__main__":
    if not run_migrations():
        sys.exit(1)
