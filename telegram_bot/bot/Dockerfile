FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (bot + backend)
COPY bot/requirements.txt .
COPY backend/requirements.txt ./backend_requirements.txt
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r backend_requirements.txt

# Copy shared module from telegram_bot root
COPY shared/ ./shared/

# Copy entire backend directory
COPY backend/ ./backend/

# Copy bot directory contents (everything from bot/) to /app/bot/
COPY bot/ ./bot/
COPY . /app
COPY knowledge/ /app/knowledge/

# Set PYTHONPATH to include both backend and current directory
ENV PYTHONPATH=/app:/app/backend

# Run bot
CMD ["python", "-m", "bot.main"]
