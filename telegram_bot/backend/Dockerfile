FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --default-timeout=100 --retries 5 -r requirements.txt

# Copy shared module and backend code
COPY shared/ ./shared/
COPY backend/app/ ./app/
COPY backend/scripts/ ./scripts/
COPY backend/migrations/ ./migrations/
COPY backend/run_migrations.py ./run_migrations.py
COPY backend/alembic.ini .

# Copy startup script and make executable
COPY scripts/start_backend.sh /app/scripts/start_backend.sh
RUN chmod +x /app/scripts/start_backend.sh

EXPOSE 8000

# ✅ FAQAT BITTA CMD — migration + uvicorn
CMD ["/app/scripts/start_backend.sh"]