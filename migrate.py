#!/usr/bin/env python3
"""
Migration Manager for MyestroEco Database
Handles versioning, execution, and rollback of SQL migrations
"""

import os
import sys
import argparse
import psycopg2
from pathlib import Path
from datetime import datetime
import subprocess

class MigrationManager:
    def __init__(self, db_host="localhost", db_port=5432, db_user="myestro", 
                 db_password="myestro_password", db_name="myestro"):
        self.db_host = db_host
        self.db_port = db_port
        self.db_user = db_user
        self.db_password = db_password
        self.db_name = db_name
        self.migrations_dir = Path(__file__).parent / "migrations" / "versions"
        self.tracking_table = "migration_history"
        
    def connect(self):
        """Connect to PostgreSQL"""
        try:
            conn = psycopg2.connect(
                host=self.db_host,
                port=self.db_port,
                user=self.db_user,
                password=self.db_password,
                database=self.db_name
            )
            return conn
        except psycopg2.Error as e:
            print(f"❌ Database connection failed: {e}")
            sys.exit(1)
    
    def init_tracking(self):
        """Initialize migration tracking table"""
        conn = self.connect()
        cur = conn.cursor()
        
        try:
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.tracking_table} (
                    id SERIAL PRIMARY KEY,
                    version VARCHAR(50) NOT NULL UNIQUE,
                    description TEXT,
                    executed_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
                    execution_time_ms INTEGER,
                    file_hash VARCHAR(64)
                )
            """)
            conn.commit()
            print(f"✓ Migration tracking table '{self.tracking_table}' ready")
        except psycopg2.Error as e:
            print(f"❌ Failed to create tracking table: {e}")
            conn.close()
            sys.exit(1)
        finally:
            cur.close()
            conn.close()
    
    def get_migration_files(self):
        """Get sorted list of migration files"""
        if not self.migrations_dir.exists():
            print(f"❌ Migrations directory not found: {self.migrations_dir}")
            sys.exit(1)
        
        migrations = sorted(self.migrations_dir.glob("*.sql"))
        return migrations
    
    def get_executed_migrations(self):
        """Get list of already executed migrations"""
        conn = self.connect()
        cur = conn.cursor()
        
        try:
            cur.execute(f"SELECT version FROM {self.tracking_table} ORDER BY version")
            executed = [row[0] for row in cur.fetchall()]
            return executed
        except psycopg2.Error:
            return []
        finally:
            cur.close()
            conn.close()
    
    def run_migration(self, migration_file):
        """Execute a single migration file"""
        conn = self.connect()
        cur = conn.cursor()
        version = migration_file.stem.split("_")[0]
        
        try:
            with open(migration_file, 'r') as f:
                sql_content = f.read()
            
            import time
            start_time = time.time()
            
            # Execute migration
            cur.execute(sql_content)
            conn.commit()
            
            execution_time = int((time.time() - start_time) * 1000)
            
            # Record migration
            cur.execute(f"""
                INSERT INTO {self.tracking_table} (version, description, execution_time_ms)
                VALUES (%s, %s, %s)
                ON CONFLICT (version) DO NOTHING
            """, (version, migration_file.name, execution_time))
            conn.commit()
            
            print(f"✓ {migration_file.name} ({execution_time}ms)")
            return True
        except Exception as e:
            print(f"❌ {migration_file.name} failed: {e}")
            conn.rollback()
            return False
        finally:
            cur.close()
            conn.close()
    
    def migrate(self):
        """Run all pending migrations"""
        print("\n🔄 Starting Database Migrations")
        print(f"Host: {self.db_host}:{self.db_port} | DB: {self.db_name}\n")
        
        self.init_tracking()
        print()
        
        migrations = self.get_migration_files()
        executed = self.get_executed_migrations()
        
        if not migrations:
            print("⚠ No migrations found")
            return
        
        executed_count = 0
        skipped_count = 0
        
        for migration_file in migrations:
            version = migration_file.stem.split("_")[0]
            if version in executed:
                print(f"⊘ Skipping {migration_file.name} (already executed)")
                skipped_count += 1
            else:
                if self.run_migration(migration_file):
                    executed_count += 1
        
        print(f"\n✅ Migration Complete!")
        print(f"Total: {len(migrations)} | Executed: {executed_count} | Skipped: {skipped_count}")
    
    def status(self):
        """Show migration status"""
        print("\n📊 Migration Status\n")
        
        migrations = self.get_migration_files()
        executed = self.get_executed_migrations()
        
        print(f"Total migrations: {len(migrations)}")
        print(f"Executed: {len(executed)}\n")
        
        conn = self.connect()
        cur = conn.cursor()
        
        try:
            cur.execute(f"""
                SELECT version, description, executed_at, execution_time_ms
                FROM {self.tracking_table}
                ORDER BY version
            """)
            
            for version, desc, executed_at, exec_time in cur.fetchall():
                print(f"✓ {version:3s} - {desc:30s} ({exec_time}ms) at {executed_at.strftime('%Y-%m-%d %H:%M:%S')}")
        finally:
            cur.close()
            conn.close()
        
        pending = [m for m in migrations if m.stem.split("_")[0] not in executed]
        if pending:
            print(f"\n⏳ Pending migrations:")
            for m in pending:
                print(f"  • {m.name}")
    
    def create_migration(self, name):
        """Create a new migration file"""
        migrations = self.get_migration_files()
        next_version = str(len(migrations) + 1).zfill(3)
        
        filename = f"{next_version}_{name}.sql"
        filepath = self.migrations_dir / filename
        
        template = f"""-- Migration: {filename}
-- Description: {name}
-- Date: {datetime.now().strftime('%Y-%m-%d')}

-- Add your SQL statements below
"""
        
        with open(filepath, 'w') as f:
            f.write(template)
        
        print(f"✓ Created migration: {filename}")
        print(f"  Path: {filepath}")

def main():
    parser = argparse.ArgumentParser(description="Database Migration Manager")
    parser.add_argument("command", choices=["migrate", "status", "create"], 
                       help="Migration command")
    parser.add_argument("--name", help="Migration name (for 'create' command)")
    
    args = parser.parse_args()
    
    # Load from environment
    manager = MigrationManager(
        db_host=os.getenv("DB_HOST", "localhost"),
        db_port=int(os.getenv("DB_PORT", "5432")),
        db_user=os.getenv("DB_USER", "myestro"),
        db_password=os.getenv("DB_PASSWORD", "myestro_password"),
        db_name=os.getenv("DB_NAME", "myestro")
    )
    
    if args.command == "migrate":
        manager.migrate()
    elif args.command == "status":
        manager.status()
    elif args.command == "create":
        if not args.name:
            print("❌ Migration name required: use --name")
            sys.exit(1)
        manager.create_migration(args.name)

if __name__ == "__main__":
    main()
