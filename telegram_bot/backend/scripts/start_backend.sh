#!/bin/bash
set -e

echo "=== Myestro Backend Startup ==="

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
for i in $(seq 1 30); do
    if python -c "import psycopg2; psycopg2.connect('${DATABASE_URL}')" 2>/dev/null; then
        echo "✓ PostgreSQL is ready!"
        break
    fi
    if [ "$i" -eq 30 ]; then
        echo "✗ PostgreSQL is not available after 30 attempts. Starting anyway..."
        break
    fi
    echo "  Waiting... ($i/30)"
    sleep 2
done

# Run database migrations
echo "Running database migrations..."
python /app/scripts/run_migrations.py

# Start the backend server
echo "Starting backend server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
