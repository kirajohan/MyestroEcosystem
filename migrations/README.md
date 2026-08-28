# Database Migrations Guide

This project uses **versioned SQL migrations** for database schema management. Each migration is a separate SQL file that tracks changes incrementally.

## Structure

```
migrations/
├── init.sql                    # Legacy: initial schema (deprecated)
├── versions/                   # Versioned migrations directory
│   ├── 001_baseline.sql        # Initial schema with all core tables
│   ├── 002_add_exam_tables.sql # Exam-related tables
│   ├── 003_add_rubrics.sql     # Rubric and grading tables
│   └── 004_add_media.sql       # Media storage and management
├── run_migrations.sh           # Linux/Mac migration runner
├── run_migrations.bat          # Windows migration runner
└── README.md                   # This file
```

## Migration Files

### 001_baseline.sql
- Creates all core tables: users, sessions, messages, knowledge docs, tests, api_logs, error_logs, audit_logs, etc.
- Initializes the migration tracking table
- Inserts default admin user

### 002_add_exam_tables.sql
- Adds exam-related tables: exam_categories, exams, exam_questions, exam_attempts
- Supports multiple exam types and CEFR levels

### 003_add_rubrics.sql
- Adds rubric system for advanced grading
- Includes rubric_criteria, rubric_levels for flexible assessment

### 004_add_media.sql
- Media storage and management: media, media_tags, media_usage
- Tracks media associations with exams and questions

## Running Migrations

### Using Docker Compose (Recommended)
```bash
docker compose up
```
- PostgreSQL automatically executes migrations on first startup
- All SQL files in `migrations/versions/` are run in alphabetical order

### Using Python Script
```bash
# Run all pending migrations
python migrate.py migrate

# Check migration status
python migrate.py status

# Create a new migration
python migrate.py create --name "add_some_feature"
```

### Using Shell Scripts

**Linux/Mac:**
```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_USER=myestro
export DB_PASSWORD=myestro_password
export DB_NAME=myestro

bash migrations/run_migrations.sh
```

**Windows:**
```batch
set DB_HOST=localhost
set DB_PORT=5432
set DB_USER=myestro
set DB_PASSWORD=myestro_password
set DB_NAME=myestro

migrations\run_migrations.bat
```

### Using psql Directly
```bash
# Single migration
psql -h localhost -p 5432 -U myestro -d myestro -f migrations/versions/001_baseline.sql

# All migrations in order
for f in migrations/versions/*.sql; do
  psql -h localhost -p 5432 -U myestro -d myestro -f "$f"
done
```

## Creating New Migrations

### Method 1: Using Python Script
```bash
python migrate.py create --name "add_new_tables"
```
This creates a new file like `005_add_new_tables.sql` with template content.

### Method 2: Manual
1. Create a new file: `migrations/versions/NNN_description.sql`
2. Use format: `NNN` = 3-digit version number (001, 002, 003, etc.)
3. Use format: `_description` = short description (underscores for spaces)
4. Add your SQL statements

Example: `migrations/versions/005_add_user_preferences.sql`

## Migration Tracking

The system uses a `migration_history` table to track executed migrations:

```sql
SELECT * FROM migration_history ORDER BY version;
```

Columns:
- `id` - Auto-increment ID
- `version` - Migration version (001, 002, etc.)
- `description` - Migration filename
- `executed_at` - Execution timestamp
- `execution_time_ms` - Time taken to execute
- `file_hash` - SHA256 hash of file content (for verification)

## Best Practices

### ✓ DO
- Keep migrations small and focused
- Use `IF NOT EXISTS` for idempotent operations
- Always test migrations on a copy of production data
- Document changes with comments in the SQL file
- Use meaningful migration names that describe what changes

### ✗ DON'T
- Modify existing migration files (breaks tracking)
- Use complex procedural logic (stick to DDL/DML)
- Mix structural changes with data changes (use separate migrations)
- Drop tables without strong reason (consider archiving instead)
- Forget to add indexes for new columns used in WHERE/JOIN clauses

## Migration Template

```sql
-- Migration: NNN_description.sql
-- Description: What this migration does
-- Date: YYYY-MM-DD

-- Create new table
CREATE TABLE IF NOT EXISTS new_table (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_new_table_name ON new_table(name);

-- Add foreign key column to existing table
ALTER TABLE users ADD COLUMN IF NOT EXISTS new_field VARCHAR(100);
```

## Troubleshooting

### Migration Failed
```bash
# Check PostgreSQL logs
docker logs myestro-postgres

# Check migration history
psql -h localhost -p 5432 -U myestro -d myestro -c "SELECT * FROM migration_history"
```

### Re-run a Migration
Migrations track by version. To re-run a migration:
```sql
DELETE FROM migration_history WHERE version = '001';
```
Then run migrations again. **Warning**: This won't roll back changes, only let you re-execute.

### Connection Issues
```bash
# Test connection
psql -h localhost -p 5432 -U myestro -d myestro -c "SELECT version();"

# Check if PostgreSQL is running
docker ps | grep postgres
```

## Integration with CI/CD

### GitHub Actions Example
```yaml
- name: Run Database Migrations
  env:
    DB_HOST: postgres
    DB_PORT: 5432
    DB_USER: myestro
    DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
    DB_NAME: myestro
  run: |
    python migrate.py migrate
```

### Docker Compose
Migrations run automatically when PostgreSQL starts:
```bash
docker compose up -d postgres
docker compose exec postgres psql -U myestro -d myestro -c "SELECT * FROM migration_history"
```

## Version History

| Version | File | Changes |
|---------|------|---------|
| 001 | baseline.sql | Initial schema with 20 core tables |
| 002 | add_exam_tables.sql | Exam management tables |
| 003 | add_rubrics.sql | Assessment rubrics system |
| 004 | add_media.sql | Media storage and management |

## Support

For questions or issues:
1. Check the [PostgreSQL documentation](https://www.postgresql.org/docs/)
2. Review existing migrations for similar patterns
3. Test changes on a development database first
