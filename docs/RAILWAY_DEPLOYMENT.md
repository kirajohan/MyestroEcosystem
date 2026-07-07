# Railway Deployment Guide for Myestro

## Prerequisites

1. **Railway.app Account** — Sign up at https://railway.app
2. **GitHub Repository** — Push all code to GitHub
3. **Environment Variables** — Prepare secrets in Railway dashboard

---

## Step 1: Create Railway Project

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login to Railway
railway login

# Create new project
railway init
```

## Step 2: Configure Services

Railway will detect and deploy three services:
- **myestro-backend** — FastAPI (port 8000)
- **myestro-bot** — Telegram bot (async, no HTTP)
- **myestro-admin** — Next.js (port 3000)

### Automatic Service Detection

Railway's `railway.toml` defines:
1. Database (PostgreSQL)
2. Cache (Redis)
3. Three application services

---

## Step 3: Set Environment Variables

In Railway dashboard, add these secrets:

### Backend Secrets
```
SECRET_KEY=<generate-secure-key>
DATABASE_URL=postgresql://...  # Auto from PostgreSQL service
REDIS_URL=redis://...          # Auto from Redis service
OPENROUTER_API_KEY=sk-...
```

### Bot Secrets
```
BOT_TOKEN=<telegram-bot-token>
CHANNEL_ID=<telegram-channel-id>
ADMIN_IDS=<comma-separated-admin-user-ids>
```

### System Secrets
```
SENTRY_DSN=https://...  # Optional: error tracking
```

---

## Step 4: Deploy

```bash
# Deploy to Railway
railway up

# Watch logs
railway logs --follow
```

Or push to GitHub with automatic Railway integration:
```bash
git push origin main
# Railway auto-deploys on push (if connected)
```

---

## Step 5: Run Database Migrations

Option A: Via Railway CLI
```bash
railway run python scripts/migrate_db.py
```

Option B: Via Web Dashboard
1. Go to Services → myestro-backend → Deploy → Shell
2. Run: `python scripts/migrate_db.py`

---

## Step 6: Verify Deployment

```bash
# Check backend health
curl https://myestro-backend-production-xxxxx.railway.app/health

# Check admin panel
https://myestro-admin-production-xxxxx.railway.app

# Check bot logs
railway logs --service myestro-bot --follow
```

---

## Monitoring & Logging

### Sentry Integration (Optional)

1. Create Sentry project at https://sentry.io
2. Add `SENTRY_DSN` secret to Railway
3. Errors automatically reported

### Railway Monitoring

View in Railway dashboard:
- **Deployment logs**
- **Service CPU/Memory**
- **Database connections**
- **Redis usage**

### Application Logs

```bash
# Tail logs
railway logs --follow

# Filter by service
railway logs --service myestro-backend --follow
railway logs --service myestro-bot --follow
```

---

## Troubleshooting

### Bot not connecting
```bash
railway logs --service myestro-bot --follow
# Check:
# - BOT_TOKEN is correct
# - Redis connection
# - API_BASE_URL reachable
```

### Database errors
```bash
# Check migrations ran
railway run psql $DATABASE_URL -c "\dt"

# Re-run migrations
railway run python scripts/migrate_db.py
```

### Admin panel showing 404
```bash
# Check Next.js build
railway logs --service myestro-admin --follow

# Verify NEXT_PUBLIC_API_URL
railway exec myestro-admin printenv | grep NEXT_PUBLIC_API_URL
```

---

## Environment Variables Reference

| Variable | Service | Type | Description |
|----------|---------|------|-------------|
| `DATABASE_URL` | Backend, Bot | Auto | PostgreSQL connection |
| `REDIS_URL` | Backend, Bot | Auto | Redis connection |
| `API_BASE_URL` | Backend, Admin | Auto | Backend public URL |
| `BOT_TOKEN` | Bot | Secret | Telegram bot token |
| `OPENROUTER_API_KEY` | Backend, Bot | Secret | AI service key |
| `CHANNEL_ID` | Bot | Secret | Telegram channel ID |
| `ADMIN_IDS` | Bot | Secret | Comma-separated admin IDs |
| `SECRET_KEY` | Backend | Secret | FastAPI secret key |
| `LOG_LEVEL` | Backend, Bot | Optional | DEBUG/INFO/WARNING |
| `PYTHONUNBUFFERED` | Backend, Bot | 1 | Real-time output |
| `NODE_ENV` | Admin | production | Next.js mode |

---

## Scaling & Performance

### Auto-Scaling (Optional)

Add to `railway.toml`:
```toml
[[plugins]]
  name = "AutoScale"
  config = {
    min_replicas = 1,
    max_replicas = 3,
    cpu_threshold = 70,
  }
```

### Database Connection Pooling

Backend uses SQLAlchemy connection pooling:
```python
pool_size = 20
max_overflow = 40
pool_pre_ping = True  # Verify connections
```

### Redis Optimization

- Cache TTLs configured in code
- Broadcast queue automatically cleaned
- FSM storage in Redis DB 1

---

## Continuous Deployment

### GitHub Integration

1. Connect GitHub repo to Railway
2. Auto-deploy on push to main branch
3. Review deployments in Railway dashboard

### Health Checks

All services have health checks:
- **Backend**: `GET /health` (200 OK)
- **Admin**: `GET /` (200 OK)
- **Bot**: Process health (memory, CPU)

---

## Cost Estimation

| Service | Estimated Cost/Month |
|---------|---------------------|
| PostgreSQL (5GB) | $5 |
| Redis (1GB) | $5 |
| Backend (512MB RAM) | $5 |
| Bot (256MB RAM) | $2 |
| Admin (512MB RAM) | $5 |
| **Total** | **~$22/month** |

---

## Support

- Railway Docs: https://docs.railway.app
- Myestro GitHub: https://github.com/kirajohan/Myestro
- Telegram: @myestro_bot
