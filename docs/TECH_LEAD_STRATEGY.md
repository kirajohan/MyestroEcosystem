# 🎯 TECH LEAD STRATEGY — Architecture & Deployment

**Role:** Senior Developer (Tech Lead)  
**Scope:** Architecture decisions, deployment strategy, system design, DevOps, monitoring  
**Duration:** 8 hours initial analysis + ongoing oversight  
**Output:** Complete deployment plan, architecture documentation, CI/CD setup

---

## 1. CURRENT STATE ANALYSIS

### 1.1 Project Inventory

```
📦 SERVICES
├─ Telegram Bot (Python, aiogram 3.x)
│  ├─ handlers/ (20 files: menu, broadcast, admin, profile, exam, etc.)
│  ├─ services/ (broadcast_worker, ai_service, content_uploader)
│  └─ middlewares/ (channel_check, registration, ai_guard)
├─ FastAPI Backend (Python, SQLAlchemy 2.0)
│  ├─ app/ (FastAPI app structure)
│  └─ alembic/ (Database migrations)
├─ Next.js Admin Panel (TypeScript/React 18)
│  ├─ app/ (App Router)
│  ├─ components/ (UI components)
│  └─ context/ (State management)
├─ PostgreSQL 15 (Main database)
├─ Redis 7 (Sessions + FSM + Queues)
└─ OpenRouter (AI fallback, optional Ollama)

📊 DATA FLOW
User Input (Telegram)
    ↓
Telegram Bot (aiogram)
    ├─ FSM Context (Redis)
    ├─ AI Generation (OpenRouter)
    └─ Database (PostgreSQL)
         ↓
Admin Dashboard (Next.js)
    ├─ FastAPI Backend (REST API)
    └─ PostgreSQL (same database)

🔌 CURRENT DEPLOYMENT
- Status: ❌ Local only (localhost)
- Railway config: ❌ Not set up
- CI/CD: ❌ No workflows
- Monitoring: ❌ No Sentry / logging
- Backups: ❌ Manual only
```

### 1.2 Critical Issues (Deployment Blockers)

```
🔴 CRITICAL (MUST FIX BEFORE DEPLOYMENT)

1. Railway Configuration
   - No railway.toml
   - No environment variables configured
   - No build/start commands defined
   - Fix: Create railway.toml, configure services
   - Time: 2 hours
   - Owner: Tech Lead

2. Database Connection (Production)
   - PostgreSQL not accessible from Railway
   - Need to use Railway PostgreSQL or set up connection pooling
   - Fix: Migrate to Railway Postgres or configure connection string
   - Time: 1 hour

3. Redis Connection (Production)
   - Redis not accessible from Railway
   - Need Redis connection pooling for concurrent bots
   - Fix: Use Railway Redis or configure external Redis URL
   - Time: 1 hour

4. Environment Secrets Management
   - .env hardcoded with secrets (BOT_TOKEN, API_KEY, etc.)
   - Will break in git repo
   - Fix: Remove .env from git, use Railway secrets
   - Time: 0.5 hours

5. Logging & Error Handling
   - No centralized logging
   - No error tracking (Sentry)
   - Can't see when things break in production
   - Fix: Add Sentry integration, structured logging
   - Time: 2 hours

🟠 HIGH PRIORITY (BREAKS FEATURES IN PRODUCTION)

1. No Health Checks
   - Can't monitor service status
   - Silent failures
   - Fix: Add /health endpoints to all services
   - Time: 1 hour

2. No Request Validation
   - Users can send large payloads, crash services
   - Fix: Add input size limits, rate limiting
   - Time: 1 hour

3. Database Migrations
   - Alembic migrations not tested on production schema
   - Fix: Test migrations locally, create rollback plan
   - Time: 2 hours
```

### 1.3 Technology Stack Evaluation

| Component | Choice | Reasoning |
|-----------|--------|-----------|
| **Hosting** | Railway | Cheap, easy Python/Node.js support, PostgreSQL included |
| **Database** | PostgreSQL 15 | Relational, proven, Railway native support |
| **Cache** | Redis 7 | Fast FSM state, pub/sub for broadcasts |
| **API Framework** | FastAPI | Async, type-safe, auto-docs |
| **Bot Framework** | aiogram 3.x | Modern, async, Telegram v6+ support |
| **Frontend** | Next.js 14 | SSR, type-safe, full-stack JS/TS |
| **AI** | OpenRouter | Reliable, fallback support, cost-effective |
| **Monitoring** | Sentry + Structured Logs | Error tracking + audit trail |
| **CI/CD** | GitHub Actions | Native GitHub integration |

---

## 2. DEPLOYMENT ARCHITECTURE

### 2.1 Production Topology

```
┌─────────────────────────────────────────────────────────────────┐
│                        RAILWAY SERVICES                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │ Telegram Bot     │  │ FastAPI Backend  │  │  Next.js     │  │
│  │ (Python)         │  │ (Python)         │  │  Admin Panel │  │
│  │                  │  │                  │  │ (TypeScript) │  │
│  │ Port: 8001       │  │ Port: 8002       │  │  Port: 3000  │  │
│  └────────┬─────────┘  └────────┬─────────┘  └──────┬───────┘  │
│           │                     │                   │           │
│           └─────────────────────┼───────────────────┘           │
│                                 │                               │
│                    ┌────────────┴────────────┐                 │
│                    │                         │                 │
│            ┌───────▼────────┐      ┌────────▼────────┐        │
│            │ PostgreSQL 15  │      │   Redis 7       │        │
│            │ (Railway DB)   │      │ (Railway Redis) │        │
│            └────────────────┘      └─────────────────┘        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

External:
├─ Telegram API (outbound only)
├─ OpenRouter API (for AI fallback)
└─ GitHub (for CI/CD webhooks)
```

### 2.2 Railway Configuration (railway.toml)

```toml
[build]
builder = "dockerfile"
dockerfilePath = "Dockerfile"

[environments.production]
name = "myestro-prod"

[[services]]
name = "telegram-bot"
runtime = "python"
buildCommand = "pip install -r telegram_bot/requirements.txt"
startCommand = "python -m bot.main"
healthcheckPath = "/health"
healthcheckInterval = 30

[[services]]
name = "fastapi-backend"
runtime = "python"
buildCommand = "pip install -r telegram_bot/requirements.txt && alembic upgrade head"
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port 8002"
healthcheckPath = "/health"
healthcheckInterval = 30

[[services]]
name = "admin-panel"
runtime = "node"
buildCommand = "cd admin && npm install && npm run build"
startCommand = "cd admin && npm run start"
healthcheckPath = "/"
healthcheckInterval = 30

[[databases]]
name = "myestro-postgres"
runtime = "postgresql"
version = "15"

[[databases]]
name = "myestro-redis"
runtime = "redis"
version = "7"
```

### 2.3 Environment Variables (Railway Secrets)

```
# Telegram
BOT_TOKEN=<SECURE: Telegram bot token>
CHANNEL_ID=-1003933846027
CHANNEL_URL=https://t.me/testmyestro

# Database (Railway auto-injects)
DATABASE_URL=<RAILWAY_POSTGRES_URL>
REDIS_URL=<RAILWAY_REDIS_URL>

# API
API_BASE_URL=https://myestro-backend.railway.app
BACKEND_URL=https://myestro-backend.railway.app
FRONTEND_URL=https://myestro-admin.railway.app

# Security
JWT_ACCESS_SECRET=<SECURE: Generate random 64-char>
JWT_REFRESH_SECRET=<SECURE: Generate random 64-char>
JWT_ACCESS_EXPIRE=1440

# AI
OPENROUTER_API_KEY=<SECURE: OpenRouter API key>
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# Logging
LOG_LEVEL=INFO
SENTRY_DSN=<SECURE: Sentry error tracking URL>

# Admin
NEXT_PUBLIC_ADMIN_PASSWORD=<SECURE: Strong password>
```

---

## 3. SCALING & PERFORMANCE

### 3.1 Database Optimization

```sql
-- Critical Indexes (add these to migrations)
CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);
CREATE INDEX IF NOT EXISTS idx_messages_thread_id ON messages(thread_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);
CREATE INDEX IF NOT EXISTS idx_broadcast_jobs_status ON broadcast_jobs(status);

-- Connection Pooling (pgBouncer - built into Railway)
-- Railway auto-configures connection pool to 20 connections
```

### 3.2 Redis Optimization

```python
# Async Redis connection pooling
redis = Redis.from_url(
    settings.REDIS_URL,
    encoding="utf-8",
    decode_responses=True,
    max_connections=50,  # Connection pool
)
```

### 3.3 Bot Concurrency

```python
# Current: Single bot instance
# Issue: Will fail under 10+ concurrent requests

# Solution: Use Redis FSM storage + message queue
# - Multiple bot instances can share FSM state via Redis
# - Broadcast jobs queued in Redis, processed sequentially
# - No race conditions, no duplicate sends
```

---

## 4. MONITORING & OBSERVABILITY

### 4.1 Sentry Integration

```python
# bot/config.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.redis import RedisIntegration

if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment="production",
        integrations=[
            FastApiIntegration(),
            RedisIntegration(),
        ],
        traces_sample_rate=0.1,  # 10% of requests
        profiles_sample_rate=0.1,
    )
```

### 4.2 Structured Logging

```python
# All logs should include context
logger.info(
    "Message sent",
    extra={
        "user_id": user_id,
        "message_type": "broadcast",
        "duration_ms": elapsed_time,
        "success": True,
    }
)

# Query logs in Railway Dashboard:
# SELECT * FROM logs WHERE user_id = 123 AND message_type = "broadcast"
```

### 4.3 Health Checks

```python
# /health endpoint (both services)
@app.get("/health")
async def health_check():
    checks = {
        "status": "ok",
        "database": await check_db(),
        "redis": await check_redis(),
        "timestamp": datetime.utcnow(),
    }
    return checks
```

---

## 5. IMPLEMENTATION PHASES

### Phase A: Preparation (2 hours)
1. Create railway.toml
2. Prepare environment variables list
3. Create Sentry project
4. Generate secure secrets (JWT, admin password)

### Phase B: Database & Infrastructure (3 hours)
1. Set up Railway PostgreSQL
2. Set up Railway Redis
3. Migrate database schema
4. Create database backups

### Phase C: Service Deployment (2 hours)
1. Deploy FastAPI backend
2. Deploy Telegram bot
3. Deploy Next.js admin panel
4. Configure service networking

### Phase D: Monitoring & Testing (1 hour)
1. Set up Sentry
2. Configure structured logging
3. Test health checks
4. Monitor first 24 hours

---

## 6. DEPLOYMENT CHECKLIST

```markdown
# Pre-Deployment
- [ ] All services have /health endpoint
- [ ] Database migrations tested locally
- [ ] Environment variables in Railway secrets (not in code)
- [ ] Sentry project created and DSN configured
- [ ] Database backups enabled
- [ ] Error rates < 1%
- [ ] Load testing: 10+ concurrent requests

# Deployment Day
- [ ] Deploy to Railway staging first (test branch)
- [ ] Run smoke tests against staging
- [ ] Get sign-off from team
- [ ] Deploy to production (main branch)
- [ ] Monitor logs in Railway Dashboard
- [ ] Set up PagerDuty alerts

# Post-Deployment (24-48 hours)
- [ ] Monitor error rate (should be <1%)
- [ ] Check database query performance
- [ ] Monitor Redis memory usage
- [ ] Verify backups running
- [ ] Check user feedback
- [ ] Document any issues
```

---

## 7. ROLLBACK PLAN

If production breaks:

```bash
# 1. Stop telegram bot (in Railway Dashboard)
# 2. Check database integrity
# 3. Review Sentry errors
# 4. Deploy previous working version
# 5. Verify all services recovering
```

---

## 8. ARCHITECTURE DECISIONS (ADRs)

### ADR-001: Redis for FSM State (ACCEPTED)
- **Decision:** Use Redis instead of file-based FSM storage
- **Rationale:** Multiple bot instances can share state
- **Trade-off:** Requires Redis connection, adds complexity
- **Impact:** Enables horizontal scaling

### ADR-002: PostgreSQL Primary Database (ACCEPTED)
- **Decision:** Use PostgreSQL for all persistent data
- **Rationale:** Relational data, ACID compliance, proven at scale
- **Trade-off:** Less flexible than NoSQL for unstructured data
- **Impact:** Easier queries, better data integrity

### ADR-003: OpenRouter for AI Fallback (ACCEPTED)
- **Decision:** Use OpenRouter as primary AI provider
- **Rationale:** Cheap, reliable, multiple model support
- **Trade-off:** External dependency, costs money
- **Impact:** Sustainable AI features without self-hosting

---

## 9. SUCCESS METRICS

- ✅ All services deployed to Railway
- ✅ Health checks returning 200 OK
- ✅ Database accessible and migrated
- ✅ Redis FSM working (users stay logged in across restarts)
- ✅ Errors tracked in Sentry
- ✅ Structured logs queryable
- ✅ Zero downtime during deployment
- ✅ < 2s response time for 99% of requests

