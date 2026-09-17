#!/bin/sh
set -e

echo "⏳ Waiting for Railway PostgreSQL..."
# Railway DB tayyor bo'lguncha kutish (max 60 sek)
for i in $(seq 1 60); do
  if python -c "
import os
import psycopg2

url = os.environ['DATABASE_URL']
# Railway public URL bo'lsa SSL qo'shish
if 'sslmode' not in url and ('rlwy.net' in url or 'railway' in url):
    sep = '&' if '?' in url else '?'
    url = f'{url}{sep}sslmode=require'

try:
    conn = psycopg2.connect(url, connect_timeout=5)
    conn.close()
    exit(0)
except:
    exit(1)
" 2>/dev/null; then
    echo "✅ Railway PostgreSQL ready"
    break
  fi
  echo "   DB not ready yet, retry $i/60..."
  sleep 1
done

echo "🔄 Running migrations..."
python run_migrations.py || {
  echo "❌ Migrations failed!"
  exit 1
}

echo "🚀 Starting backend on port ${PORT:-8000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}