# Dockerfile for Telegram Bot Service
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY telegram_bot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY telegram_bot/ ./telegram_bot/
COPY .env* ./

# Set Python path
ENV PYTHONPATH=/app/telegram_bot

# Run Bot
CMD ["python", "-m", "bot.main"]
