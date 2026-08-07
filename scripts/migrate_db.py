#!/usr/bin/env python
"""Database initialization script for Railway deployment.

Runs all migrations from migrations/ directory.
Set DATABASE_URL and run this script before starting services.
"""

import os
import sys
import subprocess
import psycopg2
from pathlib import Path

def run_migrations():
    """Run SQL migration files in order."""
    migrations_dir = Path(__file__).parent.parent / "migrations"
    
    if not migrations_dir.exists():
        print(f"Migrations directory not found: {migrations_dir}")
        return False
    
    # SQL migration files in order (init.sql MUST be first — creates users table)
    migration_files = [
        "init.sql",
        "broadcast_tables.sql",
        "inbox_tables.sql",
        "exam_tables.sql",
        "global_settings.sql",
        "logs_table.sql",
    ]
    
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("ERROR: DATABASE_URL not set")
        return False
    
    # Parse connection string
    try:
        import psycopg2
        from urllib.parse import urlparse
        
        parsed = urlparse(db_url)
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            user=parsed.username,
            password=parsed.password,
            dbname=parsed.path.lstrip('/'),
        )
        cur = conn.cursor()
        
        for migration_file in migration_files:
            filepath = migrations_dir / migration_file
            if not filepath.exists():
                print(f"⊘ Skipping {migration_file} (not found)")
                continue
            
            print(f"> Running {migration_file}...", end=" ")
            try:
                with open(filepath, 'r') as f:
                    sql = f.read()
                cur.execute(sql)
                conn.commit()
                print("OK")
            except Exception as e:
                print(f"FAILED: {e}")
                conn.rollback()
                return False
        
        cur.close()
        conn.close()
        print("\nAll migrations completed successfully")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False


def run_alembic():
    """Run Alembic migrations for backend."""
    try:
        print("Running Alembic migrations...")
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd=Path(__file__).parent / "telegram_bot" / "backend",
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("Alembic migrations completed")
            return True
        else:
            print(f"Alembic error: {result.stderr}")
            return False
    except FileNotFoundError:
        print("Alembic not found, skipping")
        return True


if __name__ == "__main__":
    print("Starting database initialization...\n")
    
    # Run SQL migrations
    if not run_migrations():
        print("\nSQL migrations failed")
        sys.exit(1)
    
    # Run Alembic
    if not run_alembic():
        print("\nAlembic migrations failed")
        sys.exit(1)
    
    print("\nDatabase initialization complete!")
    sys.exit(0)
