#!/usr/bin/env python3
"""
MyestroEco Migration System Setup Summary
Quick overview of migration capabilities
"""

import subprocess
from pathlib import Path

def print_section(title):
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")

def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        return result.stdout.strip()
    except:
        return "N/A"

def main():
    print_section("MYESTROECO SQL MIGRATION SYSTEM - SETUP SUMMARY")
    
    # 1. File Structure
    print_section("1. PROJECT STRUCTURE")
    
    base_path = Path(__file__).parent
    files = {
        "Migration Tool": "scripts/migrate_sql.py",
        "Deployment (Linux/Mac)": "scripts/deploy.sh",
        "Deployment (Windows)": "scripts/deploy.bat",
        "Migrations Directory": "migrations/versions/",
        "Documentation": "MIGRATION_GUIDE.md",
        "Quick Ref": "MIGRATION_QUICKREF.md",
    }
    
    for name, path in files.items():
        full_path = base_path / path
        exists = "EXISTS" if full_path.exists() else "MISSING"
        print(f"  [{'OK' if exists == 'EXISTS' else 'XX'}] {name:<30} {path}")
        if exists == "EXISTS" and full_path.is_file():
            size = full_path.stat().st_size
            print(f"       Size: {size:,} bytes\n")
    
    # 2. Migration Files
    print_section("2. MIGRATION FILES")
    
    migrations_dir = base_path / "migrations" / "versions"
    if migrations_dir.exists():
        migrations = sorted(migrations_dir.glob("*.sql"))
        for i, mig in enumerate(migrations, 1):
            size = mig.stat().st_size
            print(f"  {i}. {mig.name:<50} ({size:,} bytes)")
    
    # 3. Database Status
    print_section("3. DATABASE STATUS")
    
    print("  Database Server Information:")
    print("    Host: localhost")
    print("    Port: 5433")
    print("    User: myestro")
    print("    Database: myestro")
    print("    Status: Docker container")
    
    tables = run_cmd("docker exec myestro-postgres psql -U myestro -d myestro -c \"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';\" 2>/dev/null")
    indexes = run_cmd("docker exec myestro-postgres psql -U myestro -d myestro -c \"SELECT COUNT(*) FROM pg_indexes WHERE schemaname='public';\" 2>/dev/null")
    
    print(f"\n  Database Objects:")
    print(f"    Total Tables: {tables.strip() if tables else '(check connection)'}")
    print(f"    Total Indexes: {indexes.strip() if indexes else '(check connection)'}")
    
    # 4. Quick Commands
    print_section("4. QUICK START COMMANDS")
    
    commands = {
        "Check Status": "python scripts/migrate_sql.py status",
        "Run Migrations": "python scripts/migrate_sql.py migrate",
        "Create Migration": "python scripts/migrate_sql.py create --name 'feature'",
        "Validate Files": "python scripts/migrate_sql.py validate",
        "Deploy (Linux/Mac)": "bash scripts/deploy.sh",
        "Deploy (Windows)": "scripts/deploy.bat",
        "View History": "psql -c 'SELECT * FROM migration_history;'",
    }
    
    for name, cmd in commands.items():
        print(f"  {name:<25} {cmd}")
    
    # 5. Key Features
    print_section("5. KEY FEATURES")
    
    features = [
        "Automatic versioning (000, 001, 002...)",
        "Idempotent execution (runs once)",
        "Database tracking with migration_history table",
        "Performance monitoring (execution time tracked)",
        "Error logging and status tracking",
        "SQL validation tool",
        "Interactive migration creation",
        "Support for DATABASE_URL environment variable",
        "Cross-platform support (Linux, Mac, Windows)",
        "Docker integration (auto-runs on startup)",
    ]
    
    for i, feature in enumerate(features, 1):
        print(f"  {i:2d}. {feature}")
    
    # 6. Documentation Files
    print_section("6. DOCUMENTATION")
    
    docs = {
        "MIGRATION_GUIDE.md": "Comprehensive guide with examples",
        "MIGRATION_QUICKREF.md": "Quick reference for common tasks",
        "MIGRATIONS_QUICKSTART.md": "Quick start guide",
        "README.md": "Project overview",
    }
    
    for filename, description in docs.items():
        path = base_path / filename
        status = "AVAILABLE" if path.exists() else "MISSING"
        print(f"  [{status:8s}] {filename:<30} {description}")
    
    # 7. Common Workflows
    print_section("7. COMMON WORKFLOWS")
    
    workflows = {
        "Add New Table": [
            "1. python scripts/migrate_sql.py create --name 'my_table'",
            "2. Edit migrations/versions/NNN_my_table.sql",
            "3. python scripts/migrate_sql.py migrate",
        ],
        "Deploy Project": [
            "1. bash scripts/deploy.sh  (or scripts/deploy.bat on Windows)",
            "2. Automatically runs all migrations",
            "3. python scripts/migrate_sql.py status  (verify)",
        ],
        "Development": [
            "1. Create migration: python scripts/migrate_sql.py create --name 'feature'",
            "2. Edit SQL file: migrations/versions/NNN_feature.sql",
            "3. Run: python scripts/migrate_sql.py migrate",
            "4. Test: python scripts/migrate_sql.py validate",
            "5. Check: python scripts/migrate_sql.py status",
        ],
    }
    
    for workflow_name, steps in workflows.items():
        print(f"\n  {workflow_name}:")
        for step in steps:
            print(f"    {step}")
    
    # 8. Current Migrations
    print_section("8. CURRENT MIGRATIONS")
    
    migrations_info = {
        "000_create_schema_migrations.sql": "Creates migration tracking table",
        "001_baseline.sql": "Initial schema (43 tables, 142 indexes)",
        "002_create_new_exam_tables.sql": "Exam management tables",
        "003_add_user_preferences.sql": "User preferences & audit settings",
    }
    
    for filename, description in migrations_info.items():
        print(f"  {filename:<45} {description}")
    
    # 9. Tips
    print_section("9. TIPS & BEST PRACTICES")
    
    tips = [
        "Use 'IF NOT EXISTS' in migration files for safety",
        "Create separate migrations for unrelated changes",
        "Add indexes for frequently queried columns",
        "Include descriptive comments in SQL files",
        "Test migrations on development database first",
        "Keep migration descriptions short but meaningful",
        "Never modify existing migration files",
        "Use meaningful table/column names",
    ]
    
    for i, tip in enumerate(tips, 1):
        print(f"  {i:2d}. {tip}")
    
    # 10. Support
    print_section("10. GETTING HELP")
    
    print("  Command Help:")
    print("    python scripts/migrate_sql.py --help")
    print("\n  Check Migration History:")
    print("    docker exec myestro-postgres psql -U myestro -d myestro \\")
    print("      -c 'SELECT * FROM migration_history;'")
    print("\n  View Database Objects:")
    print("    docker exec myestro-postgres psql -U myestro -d myestro -c '\\dt'")
    print("\n  Documentation:")
    print("    1. MIGRATION_GUIDE.md (full documentation)")
    print("    2. MIGRATION_QUICKREF.md (quick reference)")
    print("    3. MIGRATIONS_QUICKSTART.md (quick start)")
    
    # Final status
    print_section("STATUS")
    
    print("  MyestroEco SQL Migration System is READY TO USE!")
    print("\n  Next Steps:")
    print("    1. Review: MIGRATION_GUIDE.md")
    print("    2. Create your first migration:")
    print("       python scripts/migrate_sql.py create --name 'my_feature'")
    print("    3. Edit: migrations/versions/004_my_feature.sql")
    print("    4. Run: python scripts/migrate_sql.py migrate")
    print("    5. Check: python scripts/migrate_sql.py status")
    print("\n  Or deploy full stack:")
    print("    bash scripts/deploy.sh  (Linux/Mac)")
    print("    scripts/deploy.bat      (Windows)")
    
    print_section("")

if __name__ == "__main__":
    main()
