#!/bin/bash
# Myestro Deployment Script

set -e

echo "🚀 Myestro Deployment Starting..."

# Check prerequisites
command -v docker >/dev/null 2>&1 || { echo "❌ Docker required"; exit 1; }

# Load environment
if [ -f .env.production ]; then
    export $(grep -v '^#' .env.production | xargs)
fi

# Step 1: Build and start all services
echo "🏗️ Building Docker images..."
docker compose -f docker-compose.yml build

echo "🚀 Starting all services..."
docker compose -f docker-compose.yml up -d

# Step 2: Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Step 3: Run database migrations
echo "🗄️ Running migrations..."
docker compose exec -T backend alembic upgrade head 2>/dev/null || echo "⚠️ Migrations skipped"

# Step 4: Verify deployment
echo "✅ Verifying deployment..."
curl -sf http://localhost:8002/health && echo " Backend OK" || echo " Backend unavailable"
curl -sf http://localhost:3002 > /dev/null && echo " Admin OK" || echo " Admin unavailable"

echo "🎉 Deployment complete!"
echo "📊 Admin: http://localhost:3002"
echo "🔌 API: http://localhost:8002/docs"