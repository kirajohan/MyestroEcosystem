# 🛠️ Myestro Development Implementation Strategy

> **Kompilator:** Myestro Dev Agent | **Target:** Senior Developer + Tech Team  
> **Maqsad:** Detailed code implementation guide barcha 10 phase uchun  
> **Qo'llaniladigan:** FastAPI, Aiogram 3.x, Next.js 14, PostgreSQL, Redis

---

## 📑 Table of Contents

1. [Phase 0: Whisper Removal](#phase-0-whisper-removal)
2. [Phase 1: Slash Commands](#phase-1-slash-commands)
3. [Phase 2: Channel Check & Bot Settings](#phase-2-channel-check--bot-settings)
4. [Phase 3: Broadcast System](#phase-3-broadcast-system)
5. [Phase 4: Inbox System](#phase-4-inbox-system)
6. [Phase 5: Global Settings Toggles](#phase-5-global-settings-toggles)
7. [Phase 6: Logs Dashboard](#phase-6-logs-dashboard)
8. [Phase 7: AI Chat Activation](#phase-7-ai-chat-activation)
9. [Phase 8: UI Improvements](#phase-8-ui-improvements)
10. [Phase 9: Railway Deployment](#phase-9-railway-deployment)

---

## Phase 0: Whisper Removal

### 0.1 Files to Remove/Modify

**Files to DELETE:**
- `telegram_bot/whisper_service/` — Butun folder

**Files to SEARCH (grep -r "whisper" "transcribe_voice"):**
- `telegram_bot/shared/ai_client.py`
- `telegram_bot/bot/utils/ai_client.py`
- `telegram_bot/bot/handlers/voice.py`
- `telegram_bot/bot/middlewares/`
- `.env`

### 0.2 Removal Checklist

```bash
# 1. Find all whisper references
grep -rni "whisper\|transcribe_voice\|WHISPER_SERVICE_URL" telegram_bot/

# 2. Remove from .env
# Remove line: WHISPER_SERVICE_URL=...

# 3. Remove from bot/utils/ai_client.py
# Remove: transcribe_voice(), WHISPER_SERVICE_URL export

# 4. Remove from bot/handlers/voice.py
# Replace logic with: "❌ Afsuski, faqat matn xabarlarni qabul qila olaman"

# 5. Update bot/middlewares/ (if voice content type check exists)
# Remove voice from allowed content types (if applicable)
```

### 0.3 Voice Handler Stub

**File:** `telegram_bot/bot/handlers/voice.py`

```python
from aiogram import Router, types
from aiogram.filters import Command

router = Router()

@router.message()
async def voice_handler(message: types.Message):
    """Voice messages not supported."""
    await message.answer(
        "❌ <b>Afsuski, faqat matn xabarlarni qabul qila olaman.</b>\n\n"
        "Iltimos, matnli formatda yozing yoki ↩️ <b>Orqaga</b> bosing."
    )
```

---

## Phase 1: Slash Commands Implementation

### 1.1 menu.py Handler Update Pattern

**Maqsad:** Barcha existing `F.text.in_(...)` filterlariga `Command("...")` qo'shish

**Pattern:**
```python
from aiogram.filters import Command

# ESKI (shart):
# @router.message(F.text.in_(["⚙️ Sozlamalar", ...]))
# async def msg_settings(message: types.Message, state: FSMContext): ...

# YANGI (shart):
@router.message(
    F.text.in_(["⚙️ Sozlamalar", "Settings"]) | Command("settings")
)
async def msg_settings(message: types.Message, state: FSMContext): ...
```

### 1.2 Handlers to Update (menu.py)

**Priority 1 (Critical):**
- `/profile` — User profili, balans
- `/settings` — Bot sozlamalari, til
- `/guide` — Qo'llanma
- `/about` — Biz haqimizda

**Priority 2 (High):**
- `/admin` — Admin xabari yuborish
- `/video` — Video darsliklar
- `/file` — File darsliklar
- `/language` — Til tanlash

**Priority 3 (Medium):**
- `/logout` — Chiqish
- `/ai` — AI bilan suhbat (qo'shimcha)
- `/exam` — Imtihon (qo'shimcha)

### 1.3 Implementation Checklist

```markdown
- [ ] Import `Command` filter from aiogram.filters
- [ ] Update 14 handlers with dual filters (F.text.in | Command)
- [ ] Test each slash command in Telegram (botfather /setcommands)
- [ ] Create `/commands_list.md` documentation
- [ ] Deploy to test bot
```

---

## Phase 2: Channel Check & Bot Settings

### 2.1 Environment Variables (.env)

```env
# Channel configuration (qo'shish):
CHANNEL_ID=-1001234567890  # Private channel ID (raqamda minus bilan)
CHANNEL_USERNAME=@my_english_channel  # Public channel username

# Bot settings (yangi):
BOT_GLOBAL_ENABLED=true  # Global bot switch
AI_GLOBAL_ENABLED=true   # Global AI switch
ADMIN_IDS=123456789,987654321  # Vergul bilan ajratilgan admin ID lar
```

### 2.2 Channel Check Middleware

**File:** `telegram_bot/bot/middlewares/channel_check.py`

```python
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from app.core.settings import settings
from bot.services.telegram_service import TelegramService

class ChannelCheckMiddleware(BaseMiddleware):
    """Check if user is member of required channel."""
    
    async def __call__(self, handler, event, data):
        # Faqat message va callback_query uchun
        if isinstance(event, (Message, CallbackQuery)):
            user_id = event.from_user.id if isinstance(event, Message) else event.from_user.id
            
            # Admin bo'lsa skip
            if user_id in settings.ADMIN_IDS:
                return await handler(event, data)
            
            # Channel membership tekshir
            try:
                telegram_service = TelegramService(settings.BOT_TOKEN)
                member = await telegram_service.get_chat_member(
                    settings.CHANNEL_ID,
                    user_id
                )
                if member.status not in ["member", "administrator", "creator"]:
                    if isinstance(event, Message):
                        await event.answer(
                            "❌ <b>Kanalga a'zo bo'lishingiz kerak!</b>\n\n"
                            f"🔗 <a href='https://t.me/{settings.CHANNEL_USERNAME}'>Kanalga a'zo bo'lish</a>"
                        )
                    return
            except Exception as e:
                # Log error but don't block (fallback)
                logger.error(f"Channel check failed: {e}")
        
        return await handler(event, data)
```

### 2.3 Onboarding Integration

**File:** `telegram_bot/bot/handlers/register.py` (yangilash)

```python
# registration_complete() da:
await message.answer(
    "✅ <b>Tizimga xush kelibsiz!</b>\n\n"
    "📚 Yangiliklarga va darslik yangiliklariga qo'l olish uchun:\n\n"
    f"🔗 <a href='https://t.me/{settings.CHANNEL_USERNAME}'>Kanalga a'zo bo'lish</a>",
    reply_markup=start_keyboard()  # Start keyboard qaytarish
)
```

---

## Phase 3: Broadcast System

### 3.1 Database Schema (broadcast_jobs table)

**File:** `migrations/broadcast_jobs.sql`

```sql
CREATE TABLE broadcast_jobs (
    id BIGSERIAL PRIMARY KEY,
    created_by_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,  -- HTML formatted content
    message_type VARCHAR(20) DEFAULT 'text',  -- 'text', 'photo', 'video', 'document'
    file_id VARCHAR(255),  -- Telegram file_id for media
    target_users BIGINT[] DEFAULT '{}',  -- Array of user IDs (NULL = all)
    scheduled_at TIMESTAMPTZ DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'pending',  -- 'pending', 'sending', 'completed', 'failed'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    total_users INT DEFAULT 0,
    sent_count INT DEFAULT 0,
    error_count INT DEFAULT 0
);

CREATE INDEX idx_broadcast_status ON broadcast_jobs(status);
CREATE INDEX idx_broadcast_created_at ON broadcast_jobs(created_at DESC);
```

### 3.2 FastAPI Broadcast Endpoints

**File:** `telegram_bot/backend/app/api/routes/broadcast.py` (yangi)

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.deps import require_admin
from app.core.redis_client import get_redis
from pydantic import BaseModel
from datetime import datetime
import json

router = APIRouter(prefix="/broadcast", tags=["broadcast"])

class BroadcastCreate(BaseModel):
    title: str
    content: str  # HTML formatted
    message_type: str = "text"  # text, photo, video, document
    file_id: str | None = None
    target_users: list[int] | None = None  # None = all users

@router.post("/send")
async def send_broadcast(
    payload: BroadcastCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
    redis = Depends(get_redis)
):
    """Create broadcast job and queue it."""
    
    # 1. Validate HTML content (escape special chars)
    safe_content = escape_html(payload.content)
    
    # 2. Get target users (if not specified, all users)
    if payload.target_users:
        target_ids = payload.target_users
    else:
        result = await db.execute(select(User.id))
        target_ids = [row[0] for row in result.fetchall()]
    
    # 3. Create broadcast job in DB
    job = BroadcastJob(
        created_by_id=admin.id,
        title=payload.title,
        content=safe_content,
        message_type=payload.message_type,
        file_id=payload.file_id,
        target_users=target_ids,
        total_users=len(target_ids)
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    
    # 4. Queue job in Redis
    job_data = {
        "id": job.id,
        "content": safe_content,
        "message_type": job.message_type,
        "file_id": job.file_id,
        "target_users": target_ids
    }
    await redis.lpush("myestro:broadcast:queue", json.dumps(job_data))
    
    return {"status": "queued", "job_id": job.id}

@router.get("/history")
async def get_broadcast_history(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Get broadcast job history."""
    query = select(BroadcastJob).order_by(BroadcastJob.created_at.desc())
    result = await db.execute(query)
    jobs = result.scalars().all()
    return jobs
```

### 3.3 Bot Broadcast Queue Worker

**File:** `telegram_bot/bot/services/broadcast_worker.py` (yangi)

```python
import asyncio
import json
import logging
from telegram_bot.shared.redis_client import redis
from telegram_bot.bot.utils.telegram_client import bot

logger = logging.getLogger(__name__)

async def broadcast_worker():
    """Listen for broadcast jobs in Redis queue."""
    
    while True:
        try:
            # Get job from queue (blocking wait 10 seconds)
            job_data = await redis.brpop("myestro:broadcast:queue", timeout=10)
            
            if not job_data:
                continue
            
            job = json.loads(job_data[1])  # job_data = (key, value)
            job_id = job["id"]
            target_users = job["target_users"]
            
            # Send to each user with error handling
            sent_count = 0
            error_count = 0
            
            for user_id in target_users:
                try:
                    if job["message_type"] == "text":
                        await bot.send_message(
                            user_id,
                            job["content"],
                            parse_mode="HTML"
                        )
                    elif job["message_type"] in ["photo", "video", "document"]:
                        # Use file_id from private channel
                        method = getattr(bot, f"send_{job['message_type']}")
                        await method(user_id, job["file_id"], caption=job["content"], parse_mode="HTML")
                    
                    sent_count += 1
                except Exception as e:
                    error_count += 1
                    logger.error(f"Failed to send to {user_id}: {e}")
                
                # Rate limit (avoid Telegram API throttling)
                await asyncio.sleep(0.05)  # 20 messages per second
            
            # Update job status in DB
            # ... (qo'shimcha DB update logic)
            logger.info(f"Broadcast {job_id}: {sent_count} sent, {error_count} errors")
            
        except Exception as e:
            logger.error(f"Broadcast worker error: {e}")
            await asyncio.sleep(5)

# Main bot startup'da:
# asyncio.create_task(broadcast_worker())
```

---

## Phase 4: Inbox System

### 4.1 Database Schema

**File:** `migrations/inbox_tables.sql`

```sql
CREATE TABLE inbox_messages (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    admin_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    subject VARCHAR(255),
    user_message TEXT NOT NULL,
    admin_reply TEXT,
    status VARCHAR(20) DEFAULT 'new',  -- 'new', 'read', 'replied', 'closed'
    is_read BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE inbox_message_history (
    id BIGSERIAL PRIMARY KEY,
    inbox_message_id BIGINT NOT NULL REFERENCES inbox_messages(id) ON DELETE CASCADE,
    sender_id BIGINT NOT NULL REFERENCES users(id),
    message_text TEXT NOT NULL,
    message_type VARCHAR(20) DEFAULT 'reply',  -- 'user_message', 'admin_reply'
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_inbox_user_status ON inbox_messages(user_id, status);
CREATE INDEX idx_inbox_created_at ON inbox_messages(created_at DESC);
```

### 4.2 FastAPI Inbox Endpoints

**File:** `telegram_bot/backend/app/api/routes/inbox.py` (yangi)

```python
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.deps import require_admin
from pydantic import BaseModel

router = APIRouter(prefix="/inbox", tags=["inbox"])

class InboxMessageCreate(BaseModel):
    subject: str | None = None
    message: str

class AdminReply(BaseModel):
    reply: str

@router.get("/messages")
async def get_inbox_messages(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Admin: Get all inbox messages grouped by user."""
    query = select(InboxMessage).order_by(InboxMessage.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/messages/{message_id}")
async def get_message_thread(
    message_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Get message history thread."""
    query = select(InboxMessageHistory).filter(
        InboxMessageHistory.inbox_message_id == message_id
    ).order_by(InboxMessageHistory.created_at)
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/messages/{message_id}/reply")
async def send_reply(
    message_id: int,
    payload: AdminReply,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Admin: Send reply to user."""
    
    # 1. Get inbox message
    inbox_msg = await db.get(InboxMessage, message_id)
    if not inbox_msg:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # 2. Add to history
    history = InboxMessageHistory(
        inbox_message_id=message_id,
        sender_id=admin.id,
        message_text=payload.reply,
        message_type="admin_reply"
    )
    db.add(history)
    
    # 3. Update status
    inbox_msg.status = "replied"
    inbox_msg.admin_reply = payload.reply
    inbox_msg.admin_id = admin.id
    
    # 4. Send to Telegram user
    await send_telegram_message(
        inbox_msg.user_id,
        f"💬 <b>Admin javobiga:</b>\n\n{payload.reply}",
        parse_mode="HTML"
    )
    
    await db.commit()
    return {"status": "sent"}
```

---

## Phase 5: Global Settings Toggles

### 5.1 Database Schema

**File:** `migrations/global_settings.sql`

```sql
CREATE TABLE global_settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(50) UNIQUE NOT NULL,
    value VARCHAR(255),
    description TEXT,
    updated_by BIGINT REFERENCES users(id),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO global_settings (key, description) VALUES
('BOT_ENABLED', 'Global bot on/off switch'),
('AI_ENABLED', 'Global AI on/off switch');
```

### 5.2 FastAPI Settings Endpoints

**File:** `telegram_bot/backend/app/api/routes/settings.py` (yangi)

```python
@router.get("/global")
async def get_global_settings(db: Session = Depends(get_db)):
    """Get all global settings."""
    query = select(GlobalSettings)
    result = await db.execute(query)
    return {row.key: row.value for row in result.scalars().all()}

@router.patch("/global/{setting_key}")
async def update_setting(
    setting_key: str,
    value: str,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Update global setting (admin only)."""
    setting = await db.execute(
        select(GlobalSettings).filter(GlobalSettings.key == setting_key)
    )
    setting = setting.scalar_one_or_none()
    
    if not setting:
        raise HTTPException(status_code=404)
    
    setting.value = value
    setting.updated_by = admin.id
    await db.commit()
    
    # Broadcast to all bot instances (Redis pub/sub)
    await redis.publish("settings:update", json.dumps({
        "key": setting_key,
        "value": value
    }))
    
    return {"updated": True}
```

### 5.3 Bot Settings Middleware

```python
class SettingsMiddleware(BaseMiddleware):
    """Check global settings before handler."""
    
    async def __call__(self, handler, event, data):
        # Get settings from cache or DB
        settings = await get_global_settings()
        
        # Check BOT_ENABLED
        if settings.get("BOT_ENABLED") != "true":
            user_id = event.from_user.id
            if user_id not in ADMIN_IDS:  # Allow admins always
                return  # Ignore message
        
        # Check AI_ENABLED (if AI handler)
        if "ai" in handler.__name__.lower():
            if settings.get("AI_ENABLED") != "true":
                await event.answer("🤖 AI vaqtincha o'chirilgan.")
                return
        
        return await handler(event, data)
```

---

## Phase 6: Logs Dashboard

### 6.1 Structured Logging

**File:** `telegram_bot/bot/utils/logger.py` (yangilash)

```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """Format logs as JSON for structured logging."""
    
    def format(self, record):
        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_obj)

# Configure root logger
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logging.getLogger().addHandler(handler)
```

### 6.2 Logs Table

**File:** `migrations/logs.sql`

```sql
CREATE TABLE logs (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    level VARCHAR(20),  -- INFO, WARNING, ERROR, DEBUG
    logger_name VARCHAR(255),
    message TEXT,
    module VARCHAR(255),
    function_name VARCHAR(255),
    line_number INT,
    exception TEXT,
    user_id BIGINT,
    extra_data JSONB
);

CREATE INDEX idx_logs_timestamp ON logs(timestamp DESC);
CREATE INDEX idx_logs_level ON logs(level);
```

### 6.3 FastAPI Logs Endpoint

**File:** `telegram_bot/backend/app/api/routes/logs.py` (yangi)

```python
@router.get("/logs")
async def get_logs(
    level: str | None = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Get structured logs."""
    query = select(Log).order_by(Log.timestamp.desc()).limit(limit)
    
    if level:
        query = query.filter(Log.level == level.upper())
    
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/logs/search")
async def search_logs(
    q: str,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Search logs by message."""
    query = select(Log).filter(
        Log.message.ilike(f"%{q}%")
    ).order_by(Log.timestamp.desc()).limit(50)
    
    result = await db.execute(query)
    return result.scalars().all()
```

---

## Phase 7: AI Chat Activation

### 7.1 AI Chat Handler

**File:** `telegram_bot/bot/handlers/ai_chat.py` (yangilash)

```python
from aiogram.fsm.state import State, StatesGroup
from openrouter_client import OpenRouterClient

class AIChat(StatesGroup):
    waiting_for_message = State()

@router.message(Command("ai"))
async def start_ai_chat(message: types.Message, state: FSMContext):
    """Start AI conversation."""
    settings = await get_global_settings()
    if settings.get("AI_ENABLED") != "true":
        await message.answer("🤖 AI vaqtincha o'chirilgan.")
        return
    
    await message.answer(
        "🤖 <b>AI Engla O'qituvchi</b>\n\n"
        "Menga savollar bering va men sizga javob beraman!\n\n"
        "Bosing ↩️ <b>Orqaga</b> chiqish uchun."
    )
    await state.set_state(AIChat.waiting_for_message)

@router.message(StateFilter(AIChat.waiting_for_message))
async def handle_ai_message(message: types.Message, state: FSMContext):
    """Handle user message to AI."""
    
    # Get conversation history
    history = await get_user_conversation(message.from_user.id)
    
    # Call OpenRouter
    client = OpenRouterClient(settings.OPENROUTER_API_KEY)
    response = await client.chat_completion(
        model="openai/gpt-4o-mini",
        messages=history + [{"role": "user", "content": message.text}],
        max_tokens=500,
    )
    
    # Send response
    await message.answer(response.choices[0].message.content)
    
    # Save to conversation history
    await save_conversation_message(message.from_user.id, "user", message.text)
    await save_conversation_message(message.from_user.id, "assistant", response.choices[0].message.content)
```

---

## Phase 8-9: UI & Deployment

### 8.1 Tailwind CSS Improvements (Design Strategy bilan synchronize)

See: `DESIGN_ENGINEER_STRATEGY.md` — Phase 6-7 sections

### 9.1 Railway Deployment

See: `TECH_LEAD_STRATEGY.md` — Section 2 (Production Topology)

**Key Files:**
- `railway.toml` — Service configuration
- `.env.production` — Environment secrets
- Database migration command in railway.toml

---

## ✅ Implementation Checklist Summary

- [ ] **Phase 0:** Whisper o'chirish (grep + file cleanup)
- [ ] **Phase 1:** Slash commands 14 handler'da qo'shish
- [ ] **Phase 2:** Channel check middleware + .env
- [ ] **Phase 3:** Broadcast DB + API + worker
- [ ] **Phase 4:** Inbox DB + API endpoints
- [ ] **Phase 5:** Global settings DB + endpoints + middleware
- [ ] **Phase 6:** Structured logging + dashboard
- [ ] **Phase 7:** AI chat handler + state machine
- [ ] **Phase 8:** Tailwind CSS UI improvements
- [ ] **Phase 9:** Railway deployment + testing

---

**Total Time: 82 hours | Target: Production-ready in 3-4 weeks**
