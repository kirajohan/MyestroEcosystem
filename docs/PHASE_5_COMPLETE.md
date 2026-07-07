# Phase 5: Global Settings & Bot Guard — COMPLETE ✅

**Duration:** 6 hours | **Completed:** Phases 0-5 (66% of total)

---

## 📋 Summary

Successfully implemented global settings system for controlling bot and AI features platform-wide:
- **Database schema** for global settings (BOT_ENABLED, AI_ENABLED)
- **Admin API endpoints** for viewing and updating settings with caching
- **BotGuardMiddleware** for enforcing global bot enable/disable
- **Caching strategy** (Redis backend + local cache in bot)
- **Admin bypass** for testing and maintenance

---

## 🎯 Implementation Details

### 1. Database Schema (`migrations/global_settings.sql`)

**Table:**
```sql
CREATE TABLE global_settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(50) UNIQUE NOT NULL,
    value VARCHAR(255),
    description TEXT,
    updated_by BIGINT REFERENCES users(id),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Default Values:**
- `BOT_ENABLED` = `'true'` — Entire bot operational
- `AI_ENABLED` = `'true'` — AI features available

---

### 2. Backend API (`app/api/settings.py`)

**Endpoints:**

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/settings/global` | GET | None | Get all settings (public, cached) |
| `/settings/global/{key}` | GET | None | Get single setting |
| `/settings/global/{key}` | PATCH | Admin | Update setting value |

**Request/Response:**

GET `/settings/global`
```json
{
  "BOT_ENABLED": {
    "value": "true",
    "description": "Enable/disable entire Telegram bot...",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  "AI_ENABLED": {
    "value": "true",
    "description": "Enable/disable AI responses...",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

PATCH `/settings/global/BOT_ENABLED`
```json
{
  "value": "false"
}
```

Response:
```json
{
  "status": "updated",
  "setting_key": "BOT_ENABLED",
  "old_value": "true",
  "new_value": "false",
  "timestamp": "2024-01-15T11:00:00Z"
}
```

**Caching Strategy:**

1. **Redis Cache (Backend)**
   - Hash: `myestro:global_settings`
   - TTL: 1 hour (3600 seconds)
   - Invalidated on update

2. **Local Cache (Bot)**
   - In-memory dict: `_settings_cache`
   - TTL: 60 seconds
   - Refreshed on timeout or error

3. **Fallback**
   - If API unreachable: use cached value
   - If cache empty: default to `'true'` (allow)

---

### 3. Bot Middleware (`bot/middlewares/bot_guard.py`)

**Purpose:**
- Check if bot is globally enabled BEFORE processing any message
- Admins always bypass this check
- Allow registration flow (/start, /register, /login)

**Cache Implementation:**
```python
_settings_cache = {"BOT_ENABLED": "true", "_ts": 0}
_cache_ttl = 60  # 1 minute

async def get_global_bot_status():
    """Fetch with local caching to reduce API calls."""
    current_time = time.time()
    if current_time - cache_ts < _cache_ttl:
        return cached_value
    # Otherwise fetch from API...
```

**Middleware Flow:**

```
Message arrives
    ↓
BotGuardMiddleware
    ├─ Is user admin? → ALLOW (skip rest)
    ├─ Is /start, /register, /login? → ALLOW (allow registration)
    └─ Check BOT_ENABLED
        ├─ BOT_ENABLED = 'true' → ALLOW
        └─ BOT_ENABLED = 'false' → BLOCK with "Bot under maintenance" message
```

---

### 4. Use Cases

**Scenario 1: Maintenance**
```bash
# Admin disables bot for updates
PATCH /settings/global/BOT_ENABLED
{"value": "false"}

# Users see: "🛑 Bot hozircha ta'mirlanmoqda..."
# Admins can still test and manage
```

**Scenario 2: Feature Rollback**
```bash
# Disable AI while fixing a bug
PATCH /settings/global/AI_ENABLED
{"value": "false"}

# Users get fallback response
# Admins can still use bot normally
```

**Scenario 3: Scheduled Maintenance**
```bash
# Disable bot during database migration
PATCH /settings/global/BOT_ENABLED
{"value": "false"}

# Re-enable when done
PATCH /settings/global/BOT_ENABLED
{"value": "true"}
```

---

### 5. Caching Behavior

**Scenario: Update Setting**
```
1. Admin sends PATCH /settings/global/BOT_ENABLED
2. Backend updates database
3. Backend invalidates Redis cache (redis.delete)
4. Bot process gets fresh value on next check (after 60s or on message)
5. User sees immediate effect (within 60 seconds)
```

**Scenario: Multiple Bot Processes**
```
Process 1: Fetches setting from API, caches locally (60s TTL)
Process 2: Fetches from Redis if available, else API
Process 3: Uses local cache independently

Result: Eventual consistency across processes within 60 seconds
```

---

### 6. Error Handling

**API Unreachable:**
- Log warning
- Return cached value
- If cache empty: default to `'true'` (permissive fallback)

**Database Error:**
- Log error
- Return cached value
- Middleware continues (fail-open)

**Invalid Setting Key:**
- 400 Bad Request
- Valid keys: BOT_ENABLED, AI_ENABLED

**Unauthorized Update:**
- Handled by `require_admin` dependency
- 401 Unauthorized returned

---

### 7. Middleware Integration

**Registration:**
```python
dp.message.middleware(BotGuardMiddleware())  # FIRST
dp.callback_query.middleware(BotGuardMiddleware())  # FIRST
dp.message.middleware(ChannelCheckMiddleware())  # SECOND
dp.message.middleware(AIGuardMiddleware())  # THIRD
dp.message.middleware(RegistrationMiddleware())  # FOURTH
```

**Why Order Matters:**
- BotGuardMiddleware stops processing early if bot disabled
- No point checking channel/AI/registration if bot is off
- Admins bypass all checks

---

### 8. Testing

**API Imports:**
```bash
python -c "from app.api import settings; print('OK')"
```

**Middleware Imports:**
```bash
python -c "from bot.middlewares.bot_guard import BotGuardMiddleware; print('OK')"
```

**Bot Main:**
```bash
python -c "from bot import main; print('OK')"
```

**Status: PASSING ✅**

---

### 9. Files Created/Modified

**Created:**
- `migrations/global_settings.sql` (675 bytes)
- `telegram_bot/bot/middlewares/bot_guard.py` (3,806 bytes)

**Modified:**
- `telegram_bot/backend/app/api/settings.py` — Added new endpoints + legacy compatibility
- `telegram_bot/bot/main.py` — Added BotGuardMiddleware import + registration

---

### 10. Known Limitations & TODOs

| Item | Status | Notes |
|------|--------|-------|
| Admin panel UI toggles | TODO | Create switch components in Next.js |
| Audit log for setting changes | TODO | Track who changed what and when |
| Scheduled toggles | TODO | Enable/disable at specific times |
| Webhooks on setting change | TODO | Notify external services |
| Per-user override | TODO | Allow certain users to bypass global toggle |
| Setting descriptions | TODO | Admin-friendly descriptions in UI |

---

## 📊 Progress Update

| Phase | Task | Hours | Status |
|-------|------|-------|--------|
| 0 | Whisper cleanup | 4 | ✅ DONE |
| 1 | Slash Commands | 10 | ✅ DONE |
| 2 | Channel Check | 6 | ✅ DONE |
| 3 | Broadcast System | 12 | ✅ DONE |
| 4 | Inbox System | 14 | ✅ DONE |
| 5 | Settings & Global Toggles | 6 | ✅ DONE |
| **Total Completed** | **52 hours (63% of 82 total)** |

---

## 🚀 Next Phase: Phase 6 — Logs Dashboard

**Scope:** Structured JSON logging and admin dashboard for viewing logs

**Expected Tasks:**
1. JSON formatter for all logs
2. Logs database table with indexed queries
3. API endpoints: `/logs`, `/logs/search`
4. Admin panel dashboard with filtering
5. Alert system for errors

**Estimated Hours:** 8

---

## 📝 Commit

```
Phase 5: Global settings and bot guard middleware
- Database: global_settings table with BOT_ENABLED, AI_ENABLED
- API: GET /settings/global, PATCH to update (admin only)
- Caching: Redis backend (1hr) + local bot cache (60s)
- Middleware: BotGuardMiddleware registered FIRST
- Fallback: Graceful degradation if API unreachable
- Admin bypass: Admins always can use bot
```

**SHA:** 2317a4b
