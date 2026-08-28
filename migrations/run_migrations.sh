#!/bin/bash
# Migration Runner Script
# Executes all SQL migrations in order from migrations/versions/

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
MIGRATIONS_DIR="${MIGRATIONS_DIR:-.}/migrations/versions"
MIGRATION_TRACKING_TABLE="migration_history"

# Database configuration from environment or defaults
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-myestro}"
DB_NAME="${DB_NAME:-myestro}"
DB_PASSWORD="${DB_PASSWORD:?ERROR: DB_PASSWORD not set}"

export PGPASSWORD="$DB_PASSWORD"

echo -e "${BLUE}🔄 Starting Database Migrations${NC}"
echo "Host: $DB_HOST:$DB_PORT | Database: $DB_NAME | User: $DB_USER"
echo ""

# Create migration tracking table if it doesn't exist
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<EOF
CREATE TABLE IF NOT EXISTS $MIGRATION_TRACKING_TABLE (
    id SERIAL PRIMARY KEY,
    version VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    executed_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    execution_time_ms INTEGER
);
EOF

echo -e "${GREEN}✓ Migration tracking table ready${NC}"
echo ""

# Get list of migration files
MIGRATION_FILES=$(find "$MIGRATIONS_DIR" -maxdepth 1 -name "*.sql" -type f | sort)

if [ -z "$MIGRATION_FILES" ]; then
    echo -e "${RED}✗ No migration files found in $MIGRATIONS_DIR${NC}"
    exit 1
fi

# Execute migrations
TOTAL_FILES=$(echo "$MIGRATION_FILES" | wc -l)
EXECUTED_COUNT=0
SKIPPED_COUNT=0

for MIGRATION_FILE in $MIGRATION_FILES; do
    MIGRATION_NAME=$(basename "$MIGRATION_FILE")
    VERSION_NUM=$(echo "$MIGRATION_NAME" | cut -d'_' -f1)
    
    # Check if migration already executed
    MIGRATION_EXISTS=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT EXISTS(SELECT 1 FROM $MIGRATION_TRACKING_TABLE WHERE version = '$VERSION_NUM');")
    
    if [ "$MIGRATION_EXISTS" = "t" ]; then
        echo -e "${BLUE}⊘ Skipping${NC} $MIGRATION_NAME (already executed)"
        SKIPPED_COUNT=$((SKIPPED_COUNT + 1))
    else
        echo -e "${BLUE}▶ Executing${NC} $MIGRATION_NAME..."
        
        START_TIME=$(date +%s%N)
        
        # Execute migration
        psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$MIGRATION_FILE" > /dev/null 2>&1
        
        END_TIME=$(date +%s%N)
        EXECUTION_TIME=$(( (END_TIME - START_TIME) / 1000000 ))  # Convert to milliseconds
        
        # Record migration
        psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<EOF
INSERT INTO $MIGRATION_TRACKING_TABLE (version, description, execution_time_ms)
VALUES ('$VERSION_NUM', '$MIGRATION_NAME', $EXECUTION_TIME)
ON CONFLICT (version) DO NOTHING;
EOF
        
        echo -e "${GREEN}✓ Completed${NC} $MIGRATION_NAME in ${EXECUTION_TIME}ms"
        EXECUTED_COUNT=$((EXECUTED_COUNT + 1))
    fi
done

echo ""
echo -e "${GREEN}🎉 Migration Complete!${NC}"
echo "Total migrations: $TOTAL_FILES | Executed: $EXECUTED_COUNT | Skipped: $SKIPPED_COUNT"
