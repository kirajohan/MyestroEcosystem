FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared module and backend code
COPY shared/ ./shared/
COPY backend/app/ ./app/
COPY backend/scripts/ ./scripts/
COPY backend/migrations/ ./migrations/
COPY backend/alembic.ini .

# Make startup script executable
RUN chmod +x /app/scripts/start_backend.sh

EXPOSE 8000

# Run migrations on startup, then start the server
CMD ["/app/scripts/start_backend.sh"]
