FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (context is telegram_bot/, so bot/requirements.txt)
COPY bot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared module from telegram_bot root
COPY shared/ ./shared/

# Copy bot directory contents (everything from bot/) to /app/bot/
COPY bot/ ./bot/

# Copy knowledge_base if it exists (it's inside bot/)
# Already included above, but being explicit
# COPY bot/knowledge_base/ ./knowledge_base/

# Run bot
CMD ["python", "-m", "bot.main"]
