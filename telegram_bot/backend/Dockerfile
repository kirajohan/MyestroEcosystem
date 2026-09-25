FROM python:3.12-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY telegram_bot/backend/requirements.txt .
RUN pip install --no-cache-dir --default-timeout=100 --retries 5 -r requirements.txt

# Shared module
COPY telegram_bot/shared/ ./shared/

# Backend app
COPY telegram_bot/backend/app/ ./app/
COPY telegram_bot/backend/alembic.ini .

# ✅ Migrations (root papkadan)
COPY migrations/ ./migrations/

# ✅ Scripts
COPY telegram_bot/backend/scripts/ ./scripts/

# CRLF fix + chmod
RUN sed -i 's/\r$//' /app/scripts/start_backend.sh \
    && sed -i 's/\r$//' /app/scripts/run_migrations.py \
    && sed -i 's/\r$//' /app/scripts/wait_for_db.py \
    && chmod +x /app/scripts/start_backend.sh

EXPOSE 8000

CMD ["/app/scripts/start_backend.sh"]