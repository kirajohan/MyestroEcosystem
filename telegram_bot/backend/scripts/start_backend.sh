#!/bin/sh
set -e

echo "=== Backend Startup ==="
echo "PWD: $(pwd)"
echo "Files in /app/scripts:"
ls -la /app/scripts/ 2>/dev/null || echo "scripts folder not found!"

echo ""
echo "Waiting for PostgreSQL..."
python /app/scripts/wait_for_db.py

echo ""
echo "Running migrations..."
python /app/scripts/run_migrations.py

echo ""
echo "Starting backend..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"