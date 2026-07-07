#!/bin/bash
set -e

cd "$(dirname "$0")"

echo "Installing dependencies..."
pip install --no-cache-dir -r telegram_bot/requirements.txt

echo "Starting Myestro Bot..."
cd telegram_bot
python -m bot.main
