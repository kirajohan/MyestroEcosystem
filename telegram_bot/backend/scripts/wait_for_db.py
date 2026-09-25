"""DB tayyor bo'lguncha kutadi."""
import os
import sys
import time
import psycopg2

url = os.environ.get("DATABASE_URL", "")
if not url:
    print("DATABASE_URL topilmadi!")
    sys.exit(1)

print(f"Connecting to: {url[:50]}...")

for i in range(60):
    try:
        conn = psycopg2.connect(url, connect_timeout=3)
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        conn.close()
        print("Database is ready!")
        sys.exit(0)
    except Exception as e:
        print(f"  DB not ready, retry {i + 1}/60... ({type(e).__name__})")
        time.sleep(2)

print("Database did not become ready in 120 seconds")
sys.exit(1)