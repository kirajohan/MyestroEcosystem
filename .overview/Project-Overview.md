---

## ESKI — 22/07/2026 12:50 (Asia/Tashkent, UTC+5:00)

---

## Hozirgi Holat — 22/07/2026 19:58 (Asia/Tashkent, UTC+5:00)

### 1. Loyiha Tavsifi

**Myestro** — O'zbekiston va Markaziy Osiyo bozoriga mo'ljallangan, **AI-powered** ingliz tilini o'rganish platformasi. Platforma **Myestro Ecosystem** doirasida joylashadi va quyidagi mahsulotlarni o'z ichiga oladi:

- **Myestro Teacher** — Telegram bot (AI o'qituvchi, suhbat, grammatika tuzatish, ovozli xabarlar)
- **Myestro Exam** — Onlayn imtihon tizimi (CEFR darajalash, IELTS/TOEFL/TOEFL mock)
- **Myestro Academy** — Video va file darsliklari bazasi
- **Admin Panel** — Foydalanuvchilar boshqaruvi, kontent, statistika, broadcast, inbox

Platforma foydalanuvchilarga ingliz tilini noldan o'rgatadi, xalqaro imtihonlarga (IELTS, TOEFL, CEFR) tayyorgarlik ko'rsatadi, AI bilan amaliy suhbat orqali til ko'nikmalarini oshiradi. Barcha asosiy funksiyalar **100% bepul** va ochiq.

Loyiha **Python 3.12** (FastAPI backend + aiogram 3.x bot) va **Next.js 14** (admin panel) texnologiyalari bilan ishlatilgan, **PostgreSQL 15** va **Redis 7** bazalari bilan. AI integratsiyasi **OpenRouter API** orqali amalga oshiriladi (GPT-4, Gemini, Mistral modelari).

### 2. Texnologiya Stack

| # | Qatlam | Texnologiya | Versiya | Roli |
|---|--------|-------------|---------|------|
| 1 | Backend | Python | 3.12 | FastAPI asosidagi API server |
| 2 | Backend | FastAPI | 0.115.0 | REST API + WebSocket framework |
| 3 | Backend | SQLAlchemy | 2.0.35 | ORM (sync + async) |
| 4 | Backend | asyncpg | 0.30.0 | PostgreSQL async driver |
| 5 | Backend | psycopg2-binary | 2.9.9 | PostgreSQL sync driver |
| 6 | Backend | Alembic | 1.13.0 | Database migration tool |
| 7 | Backend | Pydantic | 2.9.0 | Schema validation |
| 8 | Backend | python-jose[cryptography] | 3.3.0 | JWT token generation/verification |
| 9 | Backend | bcrypt | 4.2.0 | Password hashing (12 rounds) |
| 10 | Backend | httpx | 0.27.0 | HTTP client (AI API, Telegram API) |
| 11 | Backend | redis | 5.1.0 | Redis client (sync) |
| 12 | Backend | python-multipart | 0.0.12 | Form data parsing (file upload) |
| 13 | Backend | python-dotenv | 1.0.1 | Environment variable loading |
| 14 | Bot | aiogram | 3.12.0 | Telegram Bot API framework |
| 15 | Bot | redis[hiredis] | 5.1.0 | Redis client (async, FSM storage) |
| 16 | Bot | apscheduler | 3.10.4 | Background task scheduler |
| 17 | Bot | pytest | 8.3.3 | Testing framework |
| 18 | Bot | pytest-asyncio | 0.23.8 | Async test support |
| 19 | Frontend | Next.js | 14.2.3 | React framework (App Router) |
| 20 | Frontend | React | 18.3.1 | UI library |
| 21 | Frontend | TypeScript | 5.3.3 | Type system |
| 22 | Frontend | Tailwind CSS | 3.4.1 | CSS framework |
| 23 | Frontend | @tanstack/react-query | 5.28.0 | Server state management |
| 24 | Frontend | axios | 1.6.0 | HTTP client |
| 25 | Frontend | sonner | 1.3.0 | Toast notifications |
| 26 | Frontend | recharts | 2.10.0 | Charting library |
| 27 | Frontend | react-hook-form | 7.51.0 | Form management |
| 28 | Frontend | zod | 3.22.0 | Schema validation |
| 29 | Frontend | lucide-react | 0.346.0 | Icon library |
| 30 | Database | PostgreSQL | 15 | Primary database |
| 31 | Database | Redis | 7 | Cache, FSM, rate limiting, broadcast queue |
| 32 | AI | OpenRouter API | - | AI model gateway (GPT-4, Gemini, Mistral) |
| 33 | Deployment | Docker | - | Containerization |
| 34 | Deployment | Docker Compose | - | Multi-service orchestration |
| 35 | Deployment | Railway | - | Cloud deployment platform |

### 3. Arxitektura

#### 3.1. Umumiy Sxema

```
┌─────────────────────────────────────────────────────────┐
│                    Internet / Client                     │
└──────────────┬──────────────────────────┬───────────────┘
               │                          │
     ┌─────────▼─────────┐    ┌─────────▼─────────┐
     │   Telegram App    │    │  Web Browser      │
     │   (Bot Users)     │    │  (Admin Panel)    │
     └─────────┬─────────┘    └─────────┬─────────┘
               │                          │
               │    ┌─────────────────────┘
               │    │
          ┌────▼──────────────────────────────┐
          │         Gateway / Proxy           │
          │  (Docker Network: myestro-net)     │
          └────┬──────────────────┬───────────┘
               │                  │
    ┌──────────▼──────────┐  ┌───▼───────────────┐
    │   Backend API       │  │   Admin Panel     │
    │   (FastAPI)         │  │   (Next.js 14)    │
    │   :8000             │  │   :3000           │
    │                     │  │                   │
    │  ┌──────────────┐   │  │  ┌────────────┐  │
    │  │ API Routes   │   │  │  │ Pages      │  │
    │  │ (16 routers) │   │  │  │ (5 routes) │  │
    │  └──────────────┘   │  │  └────────────┘  │
    │  ┌──────────────┐   │  │  ┌────────────┐  │
    │  │ Services     │   │  │  │ Hooks      │  │
    │  │ (AI, Auth,   │   │  │  │ (React     │  │
    │  │  Knowledge)  │   │  │  │  Query)    │  │
    │  └──────────────┘   │  │  └────────────┘  │
    │  ┌──────────────┐   │  │  ┌────────────┐  │
    │  │ Models       │   │  │  │ Components │  │
    │  │ (14 tables)  │   │  │  │ (UI lib)   │  │
    │  └──────────────┘   │  │  └────────────┘  │
    └──┬──────────────────┘  └─────────────────┘
       │
    ┌──▼──────────────────────┐
    │   Database Layer        │
    │   ┌─────────────────┐   │
    │   │ PostgreSQL 15   │   │
    │   │ (18 tables)     │   │
    │   └─────────────────┘   │
    │   ┌─────────────────┐   │
    │   │ Redis 7         │   │
    │   │ DB 0: OTP/cache │   │
    │   │ DB 1: Bot FSM   │   │
    │   └─────────────────┘   │
    └─────────────────────────┘
               │
    ┌──────────▼──────────┐
    │   Telegram Bot      │
    │   (aiogram 3.x)     │
    │   Polling Mode      │
    │                     │
    │  ┌──────────────┐   │
    │  │ Handlers     │   │
    │  │ (17 routers) │   │
    │  └──────────────┘   │
    │  ┌──────────────┐   │
    │  │ Middlewares  │   │
    │  │ (3 guards)   │   │
    │  └──────────────┘   │
    │  ┌──────────────┐   │
    │  │ Services     │   │
    │  │ (AI,         │   │
    │  │  Broadcast)  │   │
    │  └──────────────┘   │
    └─────────────────────┘
               │
    ┌──────────▼──────────┐
    │   OpenRouter API    │
    │   (AI Models)       │
    │   GPT-4, Gemini,    │
    │   Mistral           │
    └─────────────────────┘
```

#### 3.2. Protokollar

| Manba → Maqsad | Protokol | Port | Tavsifi |
|----------------|----------|------|--------|
| Client → Backend | HTTP/HTTPS | 8002 (docker) / 8000 (dev) | REST API + WebSocket |
| Client → Admin | HTTP/HTTPS | 3002 (docker) / 3000 (dev) | Next.js admin panel |
| Bot → Backend | HTTP/HTTPS | 8002 (docker) / 8000 (dev) | Sync API (user data, messages) |
| Backend → Telegram | HTTPS | 443 | Bot API (content upload, broadcast send) |
| Bot → Telegram | HTTPS | 443 | Bot API (polling, message send) |
| Backend → OpenRouter | HTTPS | 443 | AI model API (chat completions) |
| Backend → Redis | RESP | 6380 (docker) / 6379 (dev) | Cache, OTP, broadcast queue |
| Bot → Redis | RESP | 6380 (docker) / 6379 (dev) | FSM storage, broadcast queue |
| Backend → PostgreSQL | PostgreSQL wire | 5433 (docker) / 5432 (dev) | Database queries |
| Bot → PostgreSQL | PostgreSQL wire | 5433 (docker) / 5432 (dev) | Async database queries |
| Admin → Backend | HTTP/HTTPS | 8002 (docker) / 8000 (dev) | API proxy (Next.js API routes) |
| Admin → WebSocket | WebSocket | 8002 (docker) | Real-time error notifications |

#### 3.3. Ma'lumot Oqimi (Data Flow Diagram)

**Normal Request Flow (Admin Panel → Backend):**
```
Admin Browser → Next.js API Route (/api/content) → Backend (/content)
  → CORS Middleware (allow_origins check)
    → Router/Controller (content.py)
      → Service (none — direct DB)
        → DB (ContentItem model, PostgreSQL)
          → Response → Next.js API Route → Browser
```

**Telegram Bot Polling Flow:**
```
Telegram Server → Bot (aiogram polling)
  → BotGuardMiddleware (BOT_ENABLED check via Backend API)
    → ChannelCheckMiddleware (channel subscription check)
      → AIGuardMiddleware (AI enabled check via Backend API)
        → Router/Controller (handler)
          → Service (AI service, sync service)
            → DB (async PostgreSQL) / Redis (FSM) / OpenRouter API
              → Response → Telegram Server
```

**AI Conversation Flow:**
```
User (Telegram) → Bot (ai_chat handler)
  → AI Guard Middleware (check AI enabled)
    → Bot Handler (ai_chat.py)
      → Bot AI Service (bot/utils/ai_client.py)
        → Shared AI Client (shared/ai_client.py)
          → OpenRouter API (chat/completions)
            → Fallback models (gemini → gpt-4o-mini → mistral)
              → Response → Bot Handler → User (Telegram)
```

**Bot → Backend Sync Flow:**
```
Bot Handler → Backend Sync API (/sync/user/{telegram_id})
  → Auth (none — tokenless sync endpoints)
    → Controller (sync.py)
      → DB (User model, PostgreSQL)
        → Response → Bot Handler
```

**Broadcast Flow:**
```
Admin (Next.js) → Backend Broadcast API (/broadcast/send)
  → Auth (require_admin)
    → BroadcastService.create_broadcast()
      → Redis (broadcast:{id}:progress hash)
        → Redis List (myestro:broadcast:queue)
          → Bot (BroadcastWorker — BRPOP consumer)
            → Telegram API (send_message/send_photo/etc)
              → Response → Redis (progress update) → Admin (polling)
```

**Error/Exception Flow:**
```
Client → Gateway → Backend
  → Middleware → Router
    → Xatolik yuz berdi (exception)
      → AppException Handler (JSONResponse)
        → Error log (DB/file)
        → ErrorResponse (status_code, error_code, message)
          → Client
```

### 4. Komponentlar (Har Biri Batafsil)

#### 4.1. Backend (FastAPI)

**Tavsif:** Myestro platformasining markaziy API serveri. Foydalanuvchilar, kontent, imtihonlar, AI assistent, statistika, broadcast, inbox, loglar va sozlamalar uchun RESTful API endpoint'lari. JWT autentifikatsiya, bcrypt parol hash, CORS, exception handling, WebSocket qo'llab-quvvatlanadi.

**Texnologiya:** Python 3.12, FastAPI 0.115.0, SQLAlchemy 2.0.35 (sync + async), Pydantic 2.9.0, PostgreSQL 15, Redis 7

**Arxitektura:**
```
telegram_bot/backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app creation, lifespan, CORS, routers
│   ├── config.py            # Pydantic settings (DB, Redis, JWT, OpenRouter, CORS)
│   ├── database.py          # Sync + async engines, SessionLocal, get_db deps
│   ├── api/                 # 16 API routers (endpoint handlers)
│   │   ├── __init__.py
│   │   ├── admin.py         # /admin/ai-chat — admin AI chat endpoint
│   │   ├── admin_messages.py # /admin-messages — inbox CMS (CRUD)
│   │   ├── ai_assistant.py  # /ai-assistant — AI query + log analysis
│   │   ├── auth.py          # /auth — register, login, OTP, telegram auth
│   │   ├── bot_text.py      # /bot-texts — CMS for bot messages
│   │   ├── broadcast.py     # /broadcast — broadcast job creation + status
│   │   ├── content.py       # /content — video/file upload to Telegram channel
│   │   ├── exams.py         # /exams — exam endpoints (stub)
│   │   ├── inbox.py         # /inbox — admin-user messaging system
│   │   ├── knowledge.py     # /knowledge — knowledge base categories/docs
│   │   ├── logs.py          # /logs — structured log viewing/search/stats
│   │   ├── settings.py      # /settings — global bot/AI toggle (cached)
│   │   ├── stats.py         # /stats — dashboard statistics
│   │   ├── sync.py          # /sync — bot-backend sync (tokenless)
│   │   └── users.py         # /users — user CRUD (note: backend_users.py at root)
│   ├── core/
│   │   ├── __init__.py
│   │   ├── deps.py          # Auth deps (get_current_user, require_admin, etc.)
│   │   ├── exceptions.py    # Custom exceptions (NotFoundException, etc.)
│   │   └── security.py      # JWT, bcrypt password hashing
│   ├── models/              # 14 SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── admin_message.py # AdminMessage
│   │   ├── bot_text.py      # BotText
│   │   ├── content.py       # ContentItem
│   │   ├── conversation.py  # ConversationThread, Message
│   │   ├── exam.py          # Exam, ExamSection, ExamQuestion, ExamAttempt, ExamAnswer
│   │   ├── knowledge.py     # KnowledgeCategory, KnowledgeDoc
│   │   ├── logs.py          # ApiLog, AuditLog, ErrorLog
│   │   ├── settings.py      # SystemSetting
│   │   └── user.py          # User, Session
│   ├── schemas/             # 11 Pydantic schemas
│   │   ├── __init__.py
│   │   ├── admin_message.py
│   │   ├── bot_text.py
│   │   ├── broadcast.py
│   │   ├── content.py
│   │   ├── conversation.py
│   │   ├── exam.py
│   │   ├── knowledge.py
│   │   ├── phone.py         # normalize_phone utility
│   │   ├── stats.py
│   │   └── user.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_service.py    # AI wrapper (ask_ai, analyze_error_logs, health_check)
│   │   ├── auth_service.py  # register, authenticate, OTP, telegram hash verify
│   │   └── knowledge_service.py
│   ├── websocket/
│   │   ├── __init__.py
│   │   └── admin_ws.py      # WebSocket /ws/admin (real-time error notifications)
│   ├── migrations/
│   │   └── env.py           # Alembic migration environment
│   └── tests/               # pytest tests
│       ├── __init__.py
│       ├── conftest.py
│       ├── test_auth.py
│       ├── test_exams.py
│       ├── test_security.py
│       ├── test_stats.py
│       ├── test_sync.py
│       └── test_users.py
├── scripts/
│   ├── create_admin.py
│   ├── seed_bot_texts.py
│   ├── seed_content.py
│   └── set_admin_password.py
├── requirements.txt
├── Dockerfile
└── alembic.ini
```

**Asosiy funksiyalar:**
| Funksiya | Tavsif |
|----------|--------|
| `create_app()` | FastAPI app yaratish, CORS, routers, exception handlers |
| `get_db()` | Sync DB session dependency |
| `get_async_db()` | Async DB session dependency |
| `hash_password()` | bcrypt (12 rounds) parol hash |
| `verify_password()` | bcrypt parol tekshirish |
| `create_access_token()` | JWT access token (15 min) |
| `create_refresh_token()` | JWT refresh token (7 days) |
| `verify_token()` | JWT token dekodlash |
| `get_current_user()` | JWT orqali foydalanuvchini aniqlash |
| `require_admin` | Admin/superadmin roliga tekshirish |
| `ask_ai()` | OpenRouter API so'rovi (fallback modellar) |
| `analyze_error_logs()` | AI bilan error loglarni tahlil qilish |
| `register_user()` | Yangi foydalanuvchi yaratish |
| `authenticate_user()` | Email/parol bilan autentikatsiya |
| `generate_otp()` | 6 xonali OTP yaratish (5 min TTL) |
| `verify_otp()` | OTP tekshirish |
| `verify_telegram_hash()` | Telegram login hash tekshirish |
| `normalize_phone()` | Telefon raqamini +998 formatiga keltirish |

**Method Reference (To'liq):**
| Klass | Method | Signature | Return | Tavsifi |
|-------|--------|-----------|--------|--------|
| `Settings` | `allowed_origins_list` | `() -> List[str]` | List[str] | CORS allowlist |
| `AppException` | `__init__` | `(detail: str, status_code: int)` | - | Base exception |
| `NotFoundException` | `__init__` | `(detail: str = "Resource not found")` | - | 404 exception |
| `UnauthorizedException` | `__init__` | `(detail: str = "Not authenticated")` | - | 401 exception |
| `ForbiddenException` | `__init__` | `(detail: str = "Forbidden")` | - | 403 exception |
| `ConflictException` | `__init__` | `(detail: str = "Conflict")` | - | 409 exception |
| `hash_password` | - | `(password: str) -> str` | str | bcrypt hash |
| `verify_password` | - | `(password: str, hashed: str) -> bool` | bool | bcrypt verify |
| `create_access_token` | - | `(user_id: int, email: str, role: str) -> str` | str | JWT access |
| `create_refresh_token` | - | `(user_id: int) -> str` | str | JWT refresh |
| `verify_token` | - | `(token: str, secret: str) -> Dict[str, Any]` | Dict | JWT decode |
| `get_current_user` | - | `(credentials, db) -> User` | User | Auth dependency |
| `require_role` | - | `(roles: List[str]) -> Callable` | Callable | Role checker factory |
| `ask_ai` | - | `(prompt, chat_history, system_prompt, model, temperature, max_tokens) -> str` | str | OpenRouter API |
| `analyze_error_logs` | - | `(logs: List[Dict]) -> List[Dict]` | List[Dict] | AI log analysis |
| `register_user` | - | `(db: DBSession, user_data: dict) -> User` | User | User registration |
| `authenticate_user` | - | `(db: DBSession, email: str, password: str) -> User` | User | Email/password auth |
| `authenticate_admin` | - | `(db: DBSession, email: str, password: str) -> dict` | dict | Admin auth |
| `generate_otp` | - | `(email: str, redis_client: Redis) -> str` | str | OTP generation |
| `verify_otp` | - | `(email: str, code: str, redis_client: Redis) -> bool` | bool | OTP verification |
| `verify_telegram_hash` | - | `(data: Dict, bot_token: str) -> bool` | bool | Telegram auth verify |

**Konfiguratsiya:**
```python
# .env faylida:
DATABASE_URL=postgresql://myestro:myestro_password@localhost:5433/myestro
REDIS_URL=redis://localhost:6380/0
JWT_ACCESS_SECRET=local_dev_jwt_access_secret_64chars_random_value_here_1234567890
JWT_REFRESH_SECRET=local_dev_jwt_refresh_secret_64chars_random_value_here_0987654321
JWT_ACCESS_EXPIRE=15  # minutes
JWT_REFRESH_EXPIRE=10080  # minutes (7 days)
OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
BOT_TOKEN=8999243344:AAE7K_VjKmxKJrhN7RDHLEnj_5k5eDtz5Mg
TELEGRAM_CONTENT_BASE=-1004336645032
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3002,...
```

#### 4.2. Telegram Bot (aiogram 3.x)

**Tavsif:** Myestro platformasining asosiy foydalanuvchi interfeysi. Telegram orqali AI o'qituvchi, imtihonlar, darsliklar, eslatmalar, referral, admin bilan aloqa. aiogram 3.x polling rejimda ishlaydi. 3 ta middleware (BotGuard, ChannelCheck, AIGuard) orqali xavfsizlik va global toggle'larni tekshiradi.

**Texnologiya:** Python 3.12, aiogram 3.12.0, SQLAlchemy 2.0.35 (async), asyncpg 0.30.0, redis[hiredis] 5.1.0, httpx 0.27.0, apscheduler 3.10.4

**Arxitektura:**
```
telegram_bot/bot/
├── main.py              # Bot initialization, router registration, middleware
├── config.py            # Settings (BOT_TOKEN, CHANNEL_ID, API_BASE_URL, etc.)
├── database.py          # Async engine + session (SQLAlchemy 2.0)
├── bot/
│   ├── handlers/        # 17 handler routers
│   │   ├── __init__.py
│   │   ├── academy.py     # Academy (video/file lessons)
│   │   ├── admin.py       # Admin commands
│   │   ├── ai_agent.py    # AI agent mode
│   │   ├── ai_chat.py     # AI chat (text + voice)
│   │   ├── broadcast.py   # Broadcast listener (Redis queue consumer)
│   │   ├── contact.py     # Contact sharing
│   │   ├── debug.py       # Debug commands
│   │   ├── document.py    # Document handler
│   │   ├── errors.py      # Error handler
│   │   ├── exam.py        # Exam handler
│   │   ├── inbox.py       # Inbox (user → admin messages)
│   │   ├── menu.py        # Main menu
│   │   ├── photo.py       # Photo handler
│   │   ├── profile.py     # User profile
│   │   ├── referral.py    # Referral system
│   │   ├── register.py    # Registration (legacy)
│   │   ├── registration.py # New user onboarding
│   │   ├── reminders.py   # Daily reminders
│   │   ├── start.py       # /start command
│   │   ├── sticker.py     # Sticker handler
│   │   ├── video.py       # Video handler
│   │   └── voice.py       # Voice message handler
│   ├── keyboards/
│   │   ├── __init__.py
│   │   ├── inline.py      # Inline keyboards
│   │   ├── inline_temp.py # Temporary inline keyboards
│   │   └── reply.py       # Reply keyboards
│   ├── middlewares/
│   │   ├── __init__.py
│   │   ├── ai_guard.py    # AI enabled check (global + user level)
│   │   ├── bot_guard.py   # Global bot enabled check
│   │   └── channel_check.py # Channel subscription check
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_service.py  # AI health check
│   │   └── broadcast_worker.py # Broadcast worker (Redis BRPOP consumer)
│   ├── states/
│   │   └── registration.py # FSM states for registration
│   └── utils/
│       ├── __init__.py
│       ├── ai_client.py   # Shared AI client wrapper
│       ├── ai_context.py  # AI context management
│       ├── ai_prompts.py  # AI prompts
│       ├── ai_prompts_enhanced.py # Enhanced AI prompts
│       ├── helpers.py     # Helper utilities
│       ├── i18n.py        # Internationalization (uz, ru, en)
│       └── i18n_orig.py   # Original i18n
├── requirements.txt
└── Dockerfile
```

**Komponent Tree:**
```
Bot (aiogram Dispatcher)
├── Middlewares (3)
│   ├── BotGuardMiddleware (BOT_ENABLED check)
│   ├── ChannelCheckMiddleware (channel subscription)
│   └── AIGuardMiddleware (AI enabled check)
├── Routers (17)
│   ├── errors.router
│   ├── start.router
│   ├── contact.router
│   ├── register.router
│   ├── profile.router
│   ├── menu.router
│   ├── ai_chat.router
│   ├── ai_agent.router
│   ├── registration.router
│   ├── inbox.router
│   ├── voice.router
│   ├── reminders.router
│   ├── referral.router
│   ├── academy.router
│   ├── admin.router
│   ├── photo.router
│   ├── document.router
│   ├── sticker.router
│   └── video.router
├── Services
│   ├── ai_service (health check)
│   └── broadcast_worker (Redis consumer)
└── Utils
    ├── ai_client (shared AI wrapper)
    ├── i18n (3 languages: uz, ru, en)
    └── helpers
```

**Konfiguratsiya:**
```python
# Bot config (bot/config.py):
BOT_TOKEN=8999243344:AAE7K_VjKmxKJrhN7RDHLEnj_5k5eDtz5Mg
CHANNEL_ID=""  # Not set in .env — channel check skips if empty
CHANNEL_USERNAME=testmyestro
DATABASE_URL=postgresql+asyncpg://myestro:myestro_password@localhost:5433/myestro
REDIS_URL=redis://localhost:6379/1  # Bot uses DB 1 for FSM
BACKEND_URL=http://localhost:8000
API_BASE_URL=http://localhost:8000
OPENROUTER_API_KEY=sk-or-v1-...
BOT_GLOBAL_ENABLED=true
AI_GLOBAL_ENABLED=true
ADMIN_IDS=8537015844
AI_TRIAL_LIMIT=3
```

#### 4.3. Admin Panel (Next.js 14)

**Tavsif:** Myestro platformasining boshqaruv paneli. Foydalanuvchilar, kontent, statistika, broadcast, login sahifalari. Next.js 14 App Router, Tailwind CSS, React Query, react-hook-form, Zod validation. AuthContext orqali localStorage-da sessiya saqlanadi (tokenless).

**Texnologiya:** Next.js 14.2.3, React 18.3.1, TypeScript 5.3.3, Tailwind CSS 3.4.1, @tanstack/react-query 5.28.0, axios 1.6.0, sonner 1.3.0, lucide-react 0.346.0

**Arxitektura:**
```
admin/
├── app/
│   ├── layout.tsx         # Root layout (QueryProvider, AuthProvider, Toaster)
│   ├── page.tsx           # Redirect to /login
│   ├── globals.css        # Tailwind + CSS variables
│   ├── login/
│   │   └── page.tsx       # Login form (react-hook-form)
│   ├── dashboard/
│   │   ├── layout.tsx     # AuthGuard + Sidebar + Header
│   │   └── page.tsx       # Stats cards, activity chart, CEFR pie chart
│   ├── users/
│   │   ├── layout.tsx     # Sidebar + main content
│   │   └── page.tsx       # User table, search, pagination, edit/delete
│   ├── content/
│   │   ├── layout.tsx     # AuthGuard + Sidebar + Header
│   │   └── page.tsx       # Upload form, content table, edit/delete modal
│   ├── broadcast/
│   │   ├── layout.tsx     # AuthGuard + Sidebar + Header
│   │   └── page.tsx       # Broadcast form, progress polling
│   └── api/
│       ├── content/
│       │   └── route.ts   # GET/POST /content (proxy to backend)
│       └── contents/
│           └── [id]/
│               └── route.ts # PATCH/DELETE /content/:id (proxy to backend)
├── components/
│   ├── AuthGuard.tsx      # Auth check (localStorage)
│   ├── layout/
│   │   ├── Sidebar.tsx    # Navigation (8 items, some disabled)
│   │   ├── MobileSidebar.tsx
│   │   └── Header.tsx
│   ├── dashboard/
│   │   ├── StatsCard.tsx
│   │   ├── ActivityChart.tsx
│   │   └── CEFRPieChart.tsx
│   ├── content/
│   │   ├── ContentTable.tsx
│   │   └── EditContentModal.tsx
│   ├── users/
│   │   ├── UserTable.tsx
│   │   ├── UserEditForm.tsx
│   │   └── UserDetailModal.tsx
│   ├── common/
│   │   ├── EmptyState.tsx
│   │   ├── ErrorDisplay.tsx
│   │   ├── LoadingSpinner.tsx
│   │   └── Skeleton.tsx
│   └── ui/
│       ├── Badge.tsx
│       ├── Button.tsx
│       ├── Card.tsx
│       ├── ConfirmDialog.tsx
│       ├── Dialog.tsx
│       ├── Input.tsx
│       └── MobileSidebar.tsx
├── context/
│   └── AuthContext.tsx    # Auth state (localStorage, login/logout)
├── hooks/
│   ├── useDashboard.ts    # useStats, useActivity, useCEFR
│   ├── useUsers.ts        # useUsers, useUpdateUser, useDeleteUser, useSendMessage
│   └── useContent.ts      # useContentList, useUpdateContent, useDeleteContent
├── lib/
│   ├── api.ts             # Axios instance (baseURL: localhost:8000)
│   ├── types.ts           # TypeScript interfaces (User, Login, Stats, etc.)
│   ├── broadcasttypes.ts  # Broadcast job types
│   └── utils.ts           # formatDate, cn (className merge)
├── providers/
│   └── QueryProvider.tsx  # React Query client provider
└── tests/
    └── e2e.sh
```

**Komponent Tree:**
```
App (RootLayout)
├── QueryProvider (React Query)
├── AuthProvider (localStorage auth)
├── Toaster (sonner)
├── Page (/) → redirect to /login
├── LoginPage (/login)
│   ├── Card
│   ├── Input (email, password)
│   └── Button (submit)
├── DashboardPage (/dashboard)
│   ├── AuthGuard
│   ├── Sidebar
│   ├── Header
│   ├── StatsCard (4 cards: users, messages, active, errors)
│   ├── ActivityChart (7-day message activity)
│   └── CEFRPieChart (CEFR level distribution)
├── UsersPage (/users)
│   ├── AuthGuard
│   ├── Sidebar
│   ├── Header
│   ├── Input (search)
│   ├── UserTable (with pagination)
│   ├── UserDetailModal
│   ├── UserEditForm
│   └── ConfirmDialog (delete)
├── ContentPage (/content)
│   ├── AuthGuard
│   ├── Sidebar
│   ├── Header
│   ├── Upload Form (title, description, type, file)
│   ├── ContentTable
│   ├── EditContentModal
│   └── ConfirmDialog (delete)
└── BroadcastPage (/broadcast)
    ├── AuthGuard
    ├── Sidebar
    ├── Header
    ├── Broadcast Form (message, media type, media URL, user IDs)
    └── Progress Bar (polling every 2s)
```

**API Bog'lanishlari:**
| Komponent | API Funksiya | Endpoint | Method |
|-----------|-------------|----------|--------|
| LoginPage | `api.post('/auth/admin-login')` | `/auth/admin-login` | POST |
| DashboardPage | `api.get('/stats')` | `/stats` | GET |
| DashboardPage | `api.get('/stats/activity?days=7')` | `/stats/activity` | GET |
| DashboardPage | `api.get('/stats/cefr')` | `/stats/cefr` | GET |
| UsersPage | `api.get('/users?skip=0&limit=50')` | `/users` | GET |
| UsersPage | `api.put('/users/${id}')` | `/users/:id` | PUT |
| UsersPage | `api.delete('/users/${id}')` | `/users/:id` | DELETE |
| ContentPage | `api.post('/content')` | `/content` | POST |
| ContentPage | `fetch('/api/content')` | `/api/content` (Next.js proxy) | GET |
| ContentPage | `fetch('/api/contents/${id}')` | `/api/contents/:id` (Next.js proxy) | PATCH |
| ContentPage | `fetch('/api/contents/${id}')` | `/api/contents/:id` (Next.js proxy) | DELETE |
| BroadcastPage | `fetch('/api/broadcast')` | `/api/broadcast` (Next.js proxy) | POST |
| BroadcastPage | `fetch('/api/broadcast/${id}')` | `/api/broadcast/:id` (Next.js proxy) | GET |

#### 4.4. Database (PostgreSQL + Redis)

**Tavsif:** PostgreSQL 15 asosiy ma'lumotlar bazasi (18 jadval), Redis 7 kesh, FSM, OTP, broadcast queue. PostgreSQL init.sql fayl orqali avtomatik yaratiladi. Redis DB 0 (backend) va DB 1 (bot FSM) foydalanadi.

**Arxitektura:**
```
Database Layer
├── PostgreSQL 15 (port 5433)
│   ├── users (foydalanuvchilar)
│   ├── sessions (JWT refresh token sessions)
│   ├── conversation_threads (AI suhbat threadlari)
│   ├── messages (AI suhbat xabarlari)
│   ├── knowledge_categories (bilim bazasi kategoriyalari)
│   ├── knowledge_docs (bilim bazasi hujjatlari)
│   ├── api_logs (API so'rov loglari)
│   ├── error_logs (xato loglari)
│   ├── audit_logs (audit loglari)
│   ├── system_settings (global sozlamalar)
│   ├── content_items (video/file darsliklar)
│   ├── bot_texts (CMS bot xabarlari)
│   ├── admin_messages (admin uchun foydalanuvchi xabarlari)
│   ├── broadcast_jobs (broadcast ishlar) [Phase 3]
│   ├── broadcast_history (broadcast yetkazib berish tarixi) [Phase 3]
│   ├── inbox_messages (admin-user xabar almashuvi) [Phase 4]
│   ├── inbox_message_history (xabar tarixi) [Phase 4]
│   ├── global_settings (global bot/AI toggle) [Phase 5]
│   └── logs (strbuyktural loglar) [Phase 6]
└── Redis 7 (port 6380)
    ├── DB 0: OTP, kesh, broadcast queue (backend)
    └── DB 1: FSM storage (bot)
```

#### 5.1. Ulanish

| Xizmat | Drayver | URL Format | Havza |
|--------|---------|-----------|-------|
| PostgreSQL | psycopg2 (sync) / asyncpg (async) | `postgresql://myestro:myestro_password@localhost:5433/myestro` | myestro |
| PostgreSQL | asyncpg | `postgresql+asyncpg://myestro:myestro_password@localhost:5433/myestro` | myestro |
| Redis | redis-py | `redis://localhost:6380/0` | DB 0 (backend) |
| Redis | redis-py (async) | `redis://localhost:6379/1` | DB 1 (bot FSM) |
| OpenRouter | httpx | `https://openrouter.ai/api/v1` | - |

#### 5.2. Jadvallar (To'liq DDL Formati)

**Jadval `users`:**
| Ustun | Tur | Constraint | Default | FK → Jadval | Indeks | Tavsifi |
|-------|-----|------------|---------|-------------|--------|--------|
| `id` | BIGSERIAL | PK, AUTO_INCREMENT | - | - | PK | Unique ID |
| `email` | VARCHAR(255) | NOT NULL, UNIQUE | - | - | `idx_users_email` | Email manzil |
| `password_hash` | VARCHAR(255) | NULL | - | - | - | bcrypt hash (12 rounds) |
| `full_name` | VARCHAR(255) | NOT NULL | - | - | - | Ism familiya |
| `role` | VARCHAR(20) | NOT NULL | `student` | - | `idx_users_role` | `student`/`admin`/`superadmin` |
| `cefr_level` | VARCHAR(10) | NOT NULL | `A1` | - | - | `A1`–`C2` |
| `target_level` | VARCHAR(10) | NOT NULL | `B1` | - | - | Maqsad daraja |
| `avatar_url` | TEXT | NULL | - | - | - | Avatar URL |
| `phone` | VARCHAR(50) | NULL | - | - | - | Telefon raqam (+998...) |
| `lang` | VARCHAR(10) | NOT NULL | `uz` | - | - | Interfeys tili (`uz`/`ru`/`en`) |
| `learning_lang` | VARCHAR(10) | NOT NULL | `en` | - | - | O'rganiladigan til |
| `telegram_id` | BIGINT | NULL, UNIQUE | - | - | `idx_users_telegram_id` | Telegram user ID |
| `telegram_username` | VARCHAR(255) | NULL | - | - | - | Telegram username |
| `auth_provider` | VARCHAR(20) | NOT NULL | `email` | - | - | `email`/`telegram` |
| `provider_user_id` | VARCHAR(255) | NULL | - | - | - | OAuth provider user ID |
| `is_active` | BOOLEAN | NOT NULL | `TRUE` | - | - | Faollik |
| `is_verified` | BOOLEAN | NOT NULL | `FALSE` | - | - | Email/tel verifikasiyasi |
| `profile_completed` | BOOLEAN | NOT NULL | `FALSE` | - | - | Profil to'ldirilganmi |
| `last_login_at` | TIMESTAMPTZ | NULL | - | - | - | Oxirgi kirish |
| `location` | VARCHAR(255) | NULL | - | - | - | Joylashuv |
| `ai_enabled` | BOOLEAN | NOT NULL | `TRUE` | - | - | AI yoqilganmi |
| `created_at` | TIMESTAMPTZ | NOT NULL | `NOW()` | - | - | Yaratilgan vaqt |
| `updated_at` | TIMESTAMPTZ | NOT NULL | `NOW()` | - | - | Yangilangan vaqt |
| `deleted_at` | TIMESTAMPTZ | NULL | - | - | - | O'chirilgan vaqt (soft delete) |

**Jadval `sessions`:**
| Ustun | Tur | Constraint | Default | FK → Jadval | Indeks | Tavsifi |
|-------|-----|------------|---------|-------------|--------|--------|
| `id` | UUID | PK | `gen_random_uuid()` | - | PK | Session ID |
| `user_id` | BIGINT | NOT NULL | - | `users.id` ON DELETE CASCADE | `idx_sessions_user_id` | Foydalanuvchi |
| `refresh_token` | VARCHAR(500) | NOT NULL | - | - | - | Refresh token |
| `device_info` | TEXT | NULL | - | - | - | Qurilma ma'lumotlari |
| `ip_address` | VARCHAR(45) | NULL | - | - | - | IP manzil |
| `expires_at` | TIMESTAMPTZ | NOT NULL | - | - | `idx_sessions_expires_at` | Muddati tugash |
| `is_revoked` | BOOLEAN | NOT NULL | `FALSE` | - | - | Revokatsiya qilinganmi |
| `created_at` | TIMESTAMPTZ | NOT NULL | `NOW()` | - | - | Yaratilgan vaqt |
| `revoked_at` | TIMESTAMPTZ | NULL | - | - | - | Revokatsiya vaqti |

**Jadval `conversation_threads`:**
| Ustun | Tur | Constraint | Default | FK → Jadval | Indeks | Tavsifi |
|-------|-----|------------|---------|-------------|--------|--------|
| `id` | BIGSERIAL | PK | - | - | PK | Thread ID |
| `user_id` | BIGINT | NOT NULL | - | `users.id` ON DELETE CASCADE | `idx_conversation_threads_user_id` | Foydalanuvchi |
| `title` | VARCHAR(255) | NULL | - | - | - | Thread sarlavhasi |
| `cefr_level` | VARCHAR(10) | NOT NULL | `A1` | - | - | CEFR daraja |
| `is_active` | BOOLEAN | NOT NULL | `TRUE` | - | - | Faollik |
| `telegram_thread_id` | BIGINT | NULL | - | - | - | Telegram thread ID |
| `last_sync_at` | TIMESTAMPTZ | NULL | - | - | - | Oxirgi sync vaqti |
| `created_at` | TIMESTAMPTZ | NOT NULL | `NOW()` | - | - | Yaratilgan vaqt |
| `updated_at` | TIMESTAMPTZ | NOT NULL | `NOW()` | - | - | Yangilangan vaqt |

**Jadval `messages`:**
| Ustun | Tur | Constraint | Default | FK → Jadval | Indeks | Tavsifi |
|-------|-----|------------|---------|-------------|--------|--------|
| `id` | BIGSERIAL | PK | - | - | PK | Xabar ID |
| `thread_id` | BIGINT | NOT NULL | - | `conversation_threads.id` ON DELETE CASCADE | `idx_messages_thread_id` | Thread |
| `user_id` | BIGINT | NOT NULL | - | `users.id` ON DELETE CASCADE | `idx_messages_user_id` | Foydalanuvchi |
| `role` | VARCHAR(20) | NOT NULL | `user` | - | - | `user`/`assistant` |
| `content` | TEXT | NOT NULL | - | - | - | Xabar matni |
| `content_type` | VARCHAR(20) | NOT NULL | `text` | - | - | `text`/`voice` |
| `ai_model` | VARCHAR(100) | NULL | - | - | - | AI model nomi |
| `tokens_used` | INTEGER | NULL | - | - | - | Tokenlar soni |
| `processing_time_ms` | INTEGER | NULL | - | - | - | Process vaqti (ms) |
| `cefr_level` | VARCHAR(10) | NULL | - | - | - | CEFR daraja |
| `grammar_corrections` | JSONB | NULL | - | - | - | Grammatika tuzatish |
| `vocabulary_suggestions` | JSONB | NULL | - | - | - | Leksika takliflari |
| `source` | VARCHAR(20) | NOT NULL | `telegram` | - | - | `telegram`/`api` |
| `created_at` | TIMESTAMPTZ | NOT NULL | `NOW()` | - | `idx_messages_created_at` | Yaratilgan vaqt |

**Jadval `content_items`:**
| Ustun | Tur | Constraint | Default | FK → Jadval | Indeks | Tavsifi |
|-------|-----|------------|---------|-------------|--------|--------|
| `id` | BIGSERIAL | PK | - | - | PK | Content ID |
| `title` | VARCHAR(255) | NOT NULL | - | - | - | Sarlavha |
| `description` | TEXT | NULL | - | - | - | Tavsif |
| `content_type` | VARCHAR(20) | NOT NULL | - | - | `idx_content_items_type` | `video`/`file` |
| `file_path` | TEXT | NULL | - | - | - | Fayl yo'li (NULL — Telegram file_id ishlatiladi) |
| `telegram_file_id` | VARCHAR(255) | NULL | - | - | - | Telegram file_id |
| `cefr_level` | VARCHAR(10) | NULL | - | - | `idx_content_items_cefr` | CEFR daraja |
| `order_index` | INTEGER | NOT NULL | `0` | - | - | Tartib |
| `is_active` | BOOLEAN | NOT NULL | `TRUE` | - | `idx_content_items_active` | Faollik |
| `created_at` | TIMESTAMPTZ | NOT NULL | `NOW()` | - | - | Yaratilgan vaqt |
| `updated_at` | TIMESTAMPTZ | NOT NULL | `NOW()` | - | - | Yangilangan vaqt |

**Jadval `knowledge_categories`:**
| Ustun | Tur | Constraint | Default | FK → Jadval | Indeks | Tavsifi |
|-------|-----|------------|---------|-------------|--------|--------|
| `id` | BIGSERIAL | PK | - | - | PK | Kategoriya ID |
| `name` | VARCHAR(255) | NOT NULL | - | - | - | Nomi |
| `slug` | VARCHAR(255) | NOT NULL, UNIQUE | - | - | - | Slug |
| `description` | TEXT | NULL | - | - | - | Tavsif |
| `icon` | VARCHAR(100) | NULL | - | - | - | Ikonka |
| `order_index` | INTEGER | NOT NULL | `0` | - | - | Tartib |
| `is_active` | BOOLEAN | NOT NULL | `TRUE` | - | - | Faollik |
| `created_at` | TIMESTAMPTZ | NOT NULL | `NOW()` | - | - | Yaratilgan vaqt |
| `updated_at` | TIMESTAMPTZ | NOT NULL | `NOW()` | - | - | Yangilangan vaqt |

**Jadval `knowledge_docs`:**
| Ustun | Tur | Constraint | Default | FK → Jadval | Indeks | Tavsifi |
|-------|-----|------------|---------|-------------|--------|--------|
| `id` | BIGSERIAL | PK | - | - | PK | Hujjat ID |
| `category_id` | BIGINT | NULL | - | `knowledge_categories.id` ON DELETE SET NULL | `idx_knowledge_docs_category_id` | Kategoriya |
| `title` | VARCHAR(255) | NOT NULL | - | - | - | Sarlavha |
| `slug` | VARCHAR(255) | NOT NULL, UNIQUE | - | - | - | Slug |
| `file_path` | TEXT | NOT NULL | - | - | - | Fayl yo'li |
| `cefr_level` | VARCHAR(10) | NULL | - | - | `idx_knowledge_docs_cefr_level` | CEFR daraja |
| `description` | TEXT | NULL | - | - | - | Tavsif |
| `tags` | JSONB | NULL | - | - | - | Teglar |
| `is_active` | BOOLEAN | NOT NULL | `TRUE` | - | - | Faollik |
| `created_at` | TIMESTAMPTZ | NOT NULL | `NOW()` | - | - | Yaratilgan vaqt |
| `updated_at` | TIMESTAMPTZ | NOT NULL | `NOW()` | - | - | Yangilangan vaqt |

**Jadval `system_settings`:**
| Ustun | Tur | Constraint | Default | FK → Jadval | Indeks | Tavsifi |
|-------|-----|------------|---------|-------------|--------|--------|
| `id` | BIGSERIAL | PK | - | - | PK | Setting ID |
| `key` | VARCHAR(255) | NOT NULL, UNIQUE | - | - | `idx_system_settings_key` | Kalit |
| `value` | TEXT | NOT NULL | - | - | - | Qiymat |
| `description` | TEXT | NULL | - | - | - | Tavsif |
| `created_at` | TIMESTAMPTZ | NOT NULL | `NOW()` | - | - | Yaratilgan vaqt |
| `updated_at` | TIMESTAMPTZ | NOT NULL | `NOW()` | - | - | Yangilangan vaqt |

**Jadval `bot_texts`:**
| Ustun | Tur | Constraint | Default | FK → Jadval | Indeks | Tavsifi |
|-------|-----|------------|---------|-------------|--------|--------|
| `id` | BIGSERIAL | PK | - | - | PK | Text ID |
| `key` | VARCHAR(100) | NOT NULL | - | - | `idx_bot_texts_key` | Kalit (`section.subsection.element`) |
| `lang` | VARCHAR(10) | NOT NULL | `uz` | - | `idx_bot_texts_lang` | Tili (`uz`/`ru`/`en`) |
| `text` | TEXT | NOT NULL | - | - | - | Matn (HTML) |
| `updated_at` | TIMESTAMPTZ | NOT NULL | `NOW()` | - | - | Yangilangan vaqt |

**Jadval `admin_messages`:**
| Ustun | Tur | Constraint | Default | FK → Jadval | Indeks | Tavsifi |
|-------|-----|------------|---------|-------------|--------|--------|
| `id` | BIGSERIAL | PK | - | - | PK | Xabar ID |
| `user_id` | BIGINT | NULL | - | `users.id` ON DELETE SET NULL | `idx_admin_messages_user_id` | Foydalanuvchi |
| `user_telegram_id` | BIGINT | NULL | - | - | - | Telegram ID |
| `user_name` | VARCHAR(255) | NULL | - | - | - | Foydalanuvchi nomi |
| `content_type` | VARCHAR(20) | NOT NULL | `text` | - | - | `text`/`photo`/`voice`/`document`/`video`/`sticker` |
| `text` | TEXT | NULL | - | - | - | Matn |
| `file_id` | VARCHAR(255) | NULL | - | - | - | Telegram file_id |
| `is_read` | BOOLEAN | NOT NULL | `FALSE` | - | `idx_admin_messages_is_read` | O'qilganmi |
| `is_replied` | BOOLEAN | NOT NULL | `FALSE` | - | - | Javob berilganmi |
| `admin_reply` | TEXT | NULL | - | - | - | Admin javobi |
| `created_at` | TIMESTAMPTZ | NOT NULL | `NOW()` | - | `idx_admin_messages_created_at` | Yaratilgan vaqt |

**Jadval `exams`:**
| Ustun | Tur | Constraint | Default | FK → Jadval | Indeks | Tavsifi |
|-------|-----|------------|---------|-------------|--------|--------|
| `id` | BIGSERIAL | PK | - | - | PK | Imtihon ID |
| `title` | VARCHAR(255) | NOT NULL | - | - | - | Sarlavha |
| `description` | TEXT | NULL | - | - | - | Tavsif |
| `cefr_level` | VARCHAR(10) | NOT NULL | - | - | - | CEFR daraja |
| `status` | VARCHAR(20) | NOT NULL | `draft` | - | - | `draft`/`published`/`archived` |
| `total_duration` | INTEGER | NOT NULL | `0` | - | - | Umumiy davomiylik (min) |
| `reading_duration` | INTEGER | NOT NULL | `0` | - | - | O'qish davomiylik |
| `listening_duration` | INTEGER | NOT NULL | `0` | - | - | Eshitish davomiylik |
| `speaking_duration` | INTEGER | NOT NULL | `0` | - | - | So'zlashish davomiylik |
| `writing_duration` | INTEGER | NOT NULL | `0` | - | - | Yozish davomiylik |
| `ownership_type` | VARCHAR(20) | NOT NULL | `owned` | - | - | `owned`/`partner` |
| `partner_name` | VARCHAR(255) | NULL | - | - | - | Partner nomi |
| `pdf_url` | TEXT | NULL | - | - | - | PDF URL |
| `mp3_url` | TEXT | NULL | - | - | - | MP3 URL |
| `passing_score` | DECIMAL(5,2) | NULL | - | - | - | O'tish balli |
| `max_score` | DECIMAL(5,2) | NULL | - | - | - | Maksimal ball |
| `version` | INTEGER | NOT NULL | `1` | - | - | Versiya |
| `is_sample` | BOOLEAN | NOT NULL | `FALSE` | - | - | Namuna imtihonmi |
| `is_active` | BOOLEAN | NOT NULL | `TRUE` | - | - | Faollik |
| `attempt_limit` | INTEGER | NOT NULL | `1` | - | - | Urinish limiti |
| `created_by` | BIGINT | NULL | - | `users.id` ON DELETE SET NULL | - | Yaratgan foydalanuvchi |
| `created_at` | TIMESTAMPTZ | NOT NULL | `NOW()` | - | - | Yaratilgan vaqt |
| `updated_at` | TIMESTAMPTZ | NOT NULL | `NOW()` | - | - | Yangilangan vaqt |
| `deleted_at` | TIMESTAMPTZ | NULL | - | - | - | O'chirilgan vaqt |

**Jadval `api_logs`:**
| Ustun | Tur | Constraint | Default | FK → Jadval | Indeks | Tavsifi |
|-------|-----|------------|---------|-------------|--------|--------|
| `id` | BIGSERIAL | PK | - | - | PK | Log ID |
| `user_id` | BIGINT | NULL | - | `users.id` ON DELETE SET NULL | `idx_api_logs_user_id` | Foydalanuvchi |
| `endpoint` | VARCHAR(500) | NOT NULL | - | - | `idx_api_logs_endpoint` | Endpoint |
| `method` | VARCHAR(10) | NOT NULL | - | - | - | HTTP method |
| `status_code` | INTEGER | NOT NULL | - | - | - | Status kod |
| `response_time_ms` | INTEGER | NULL | - | - | - | Javob vaqti (ms) |
| `ip_address` | VARCHAR(45) | NULL | - | - | - | IP manzil |
| `user_agent` | TEXT | NULL | - | - | - | User agent |
| `request_body` | JSONB | NULL | - | - | - | Request body |
| `response_body` | JSONB | NULL | - | - | - | Response body |
| `created_at` | TIMESTAMPTZ | NOT NULL | `NOW()` | - | `idx_api_logs_created_at` | Yaratilgan vaqt |

**Jadval `error_logs`:**
| Ustun | Tur | Constraint | Default | FK → Jadval | Indeks | Tavsifi |
|-------|-----|------------|---------|-------------|--------|--------|
| `id` | BIGSERIAL | PK | - | - | PK | Xato ID |
| `service` | VARCHAR(100) | NOT NULL | - | - | `idx_error_logs_service` | Xizmat |
| `error_type` | VARCHAR(255) | NOT NULL | - | - | - | Xato turi |
| `error_message` | TEXT | NOT NULL | - | - | - | Xato xabari |
| `stack_trace` | TEXT | NULL | - | - | - | Stack trace |
| `cause` | TEXT | NULL | - | - | - | Sababi |
| `solution` | TEXT | NULL | - | - | - | Yechim |
| `is_fixed` | BOOLEAN | NOT NULL | `FALSE` | - | `idx_error_logs_is_fixed` | Tuzilganmi |
| `severity` | VARCHAR(20) | NOT NULL | `error` | - | `idx_error_logs_severity` | `error`/`warning`/`critical` |
| `user_id` | BIGINT | NULL | - | `users.id` ON DELETE SET NULL | - | Foydalanuvchi |
| `metadata` | JSONB | NULL | - | - | - | Qo'shimcha ma'lumot |
| `created_at` | TIMESTAMPTZ | NOT NULL | `NOW()` | - | `idx_error_logs_created_at` | Yaratilgan vaqt |
| `fixed_at` | TIMESTAMPTZ | NULL | - | - | - | Tuzilgan vaqt |

**Jadval `audit_logs`:**
| Ustun | Tur | Constraint | Default | FK → Jadval | Indeks | Tavsifi |
|-------|-----|------------|---------|-------------|--------|--------|
| `id` | BIGSERIAL | PK | - | - | PK | Audit ID |
| `user_id` | BIGINT | NULL | - | `users.id` ON DELETE SET NULL | `idx_audit_logs_user_id` | Foydalanuvchi |
| `action` | VARCHAR(100) | NOT NULL | - | - | `idx_audit_logs_action` | Amallar |
| `resource` | VARCHAR(255) | NULL | - | - | - | Resurs |
| `details` | JSONB | NULL | - | - | - | Detallar |
| `ip_address` | VARCHAR(45) | NULL | - | - | - | IP manzil |
| `user_agent` | TEXT | NULL | - | - | - | User agent |
| `severity` | VARCHAR(20) | NOT NULL | `info` | - | `idx_audit_logs_severity` | `info`/`warning`/`error` |
| `created_at` | TIMESTAMPTZ | NOT NULL | `NOW()` | - | `idx_audit_logs_created_at` | Yaratilgan vaqt |

**Jadval `broadcast_jobs` (Phase 3):**
| Ustun | Tur | Constraint | Default | FK → Jadval | Indeks | Tavsifi |
|-------|-----|------------|---------|-------------|--------|--------|
| `id` | BIGSERIAL | PK | - | - | PK | Job ID |
| `created_by_id` | BIGINT | NOT NULL | - | `users.id` ON DELETE CASCADE | `idx_broadcast_jobs_created_by` | Yaratgan admin |
| `title` | VARCHAR(255) | NOT NULL | - | - | - | Sarlavha |
| `content` | TEXT | NOT NULL | - | - | - | Kontent (HTML) |
| `message_type` | VARCHAR(20) | NOT NULL | `text` | - | - | `text`/`photo`/`video`/`document` |
| `file_id` | VARCHAR(255) | NULL | - | - | - | Telegram file_id |
| `target_users` | BIGINT[] | NOT NULL | `'{}'` | - | - | Foydalanuvchi ID massivi |
| `scheduled_at` | TIMESTAMPTZ | NOT NULL | `NOW()` | - | - | Rejalashtirilgan vaqt |
| `status` | VARCHAR(20) | NOT NULL | `pending` | - | `idx_broadcast_jobs_status` | `pending`/`queued`/`sending`/`completed`/`failed` |
| `created_at` | TIMESTAMPTZ | NOT NULL | `NOW()` | - | `idx_broadcast_jobs_created_at` | Yaratilgan vaqt |
| `updated_at` | TIMESTAMPTZ | NOT NULL | `NOW()` | - | - | Yangilangan vaqt |
| `total_users` | INTEGER | NOT NULL | `0` | - | - | Umumiy foydalanuvchilar |
| `sent_count` | INTEGER | NOT NULL | `0` | - | - | Yuborilganlar |
| `error_count` | INTEGER | NOT NULL | `0` | - | - | Xatolar |
| `error_message` | TEXT | NULL | - | - | - | Xato xabari |

**Jadval `inbox_messages` (Phase 4):**
| Ustun | Tur | Constraint | Default | FK → Jadval | Indeks | Tavsifi |
|-------|-----|------------|---------|-------------|--------|--------|
| `id` | BIGSERIAL | PK | - | - | PK | Xabar ID |
| `user_id` | BIGINT | NOT NULL | - | `users.id` ON DELETE CASCADE | `idx_inbox_user_status` | Foydalanuvchi |
| `admin_id` | BIGINT | NULL | - | `users.id` ON DELETE SET NULL | - | Admin |
| `subject` | VARCHAR(255) | NULL | - | - | - | Mavzu |
| `user_message` | TEXT | NOT NULL | - | - | - | Foydalanuvchi xabari |
| `admin_reply` | TEXT | NULL | - | - | - | Admin javobi |
| `status` | VARCHAR(20) | NOT NULL | `new` | - | - | `new`/`read`/`replied`/`closed` |
| `is_read` | BOOLEAN | NOT NULL | `false` | - | - | O'qilganmi |
| `created_at` | TIMESTAMPTZ | NOT NULL | `NOW()` | - | `idx_inbox_created_at` | Yaratilgan vaqt |
| `updated_at` | TIMESTAMPTZ | NOT NULL | `NOW()` | - | - | Yangilangan vaqt |

**Jadval `global_settings` (Phase 5):**
| Ustun | Tur | Constraint | Default | FK → Jadval | Indeks | Tavsifi |
|-------|-----|------------|---------|-------------|--------|--------|
| `id` | SERIAL | PK | - | - | PK | Setting ID |
| `key` | VARCHAR(50) | NOT NULL, UNIQUE | - | - | `idx_global_settings_key` | Kalit (`BOT_ENABLED`/`AI_ENABLED`) |
| `value` | VARCHAR(255) | NULL | - | - | - | Qiymat (`true`/`false`) |
| `description` | TEXT | NULL | - | - | - | Tavsif |
| `updated_by` | BIGINT | NULL | - | `users.id` ON DELETE SET NULL | - | Yangilagan admin |
| `updated_at` | TIMESTAMPTZ | NOT NULL | `NOW()` | - | - | Yangilangan vaqt |

**Jadval `logs` (Phase 6):**
| Ustun | Tur | Constraint | Default | FK → Jadval | Indeks | Tavsifi |
|-------|-----|------------|---------|-------------|--------|--------|
| `id` | BIGSERIAL | PK | - | - | PK | Log ID |
| `timestamp` | TIMESTAMPTZ | NOT NULL | `NOW()` | - | `idx_logs_timestamp` | Vaqt |
| `level` | VARCHAR(20) | NOT NULL | - | - | `idx_logs_level` | `INFO`/`WARNING`/`ERROR`/`DEBUG`/`CRITICAL` |
| `logger_name` | VARCHAR(255) | NULL | - | - | `idx_logs_logger_name` | Logger nomi |
| `message` | TEXT | NULL | - | - | - | Xabar |
| `module` | VARCHAR(255) | NULL | - | - | - | Modul |
| `function_name` | VARCHAR(255) | NULL | - | - | - | Funksiya |
| `line_number` | INTEGER | NULL | - | - | - | Satr raqami |
| `exception` | TEXT | NULL | - | - | - | Exception |
| `user_id` | BIGINT | NULL | - | `users.id` ON DELETE SET NULL | `idx_logs_user_id` | Foydalanuvchi |
| `extra_data` | JSONB | NULL | - | - | - | Qo'shimcha ma'lumot |
| `created_at` | TIMESTAMPTZ | NOT NULL | `NOW()` | - | - | Yaratilgan vaqt |

**Composite Indexes:**
- `idx_logs_timestamp_level` ON `logs` (`timestamp` DESC, `level`)

#### 5.3. Enum Turlar
```sql
-- ENUM turlar ishlatilmaydi — barchasi VARCHAR sifatida saqlanadi
-- role: 'student', 'admin', 'superadmin'
-- cefr_level: 'A1', 'A2', 'B1', 'B2', 'C1', 'C2'
-- auth_provider: 'email', 'telegram'
-- content_type: 'video', 'file', 'text'
-- message_type: 'text', 'photo', 'video', 'document'
-- status (exams): 'draft', 'published', 'archived'
-- status (broadcast): 'pending', 'queued', 'sending', 'completed', 'failed'
-- status (inbox): 'new', 'read', 'replied', 'closed'
-- status (exam_attempt): 'in_progress', 'submitted', 'graded'
-- severity: 'info', 'warning', 'error', 'critical'
-- content_type (admin_messages): 'text', 'photo', 'voice', 'document', 'video', 'sticker'
-- role: 'student', 'admin', 'superadmin'
-- cefr_level: 'A1', 'A2', 'B1', 'B2', 'C1', 'C2'
-- auth_provider: 'email', 'telegram'
-- content_type: 'video', 'file', 'text'
-- message_type: 'text', 'photo', 'video', 'document'
```

#### 5.4. Redis (Agar ishlatilsa)
| Kalit Pattern | Maqsad | TTL | DB | Format |
|---------------|--------|-----|-----|--------|
| `otp:{email}` | OTP kod saqlash | 300s (5 min) | 0 | String (6 xonali kod) |
| `broadcast:{id}:progress` | Broadcast progress tracking | 86400s (7 kun) | 0 | Hash (status, total, sent, failed, title, created_at, admin_id) |
| `myestro:broadcast:queue` | Broadcast job queue | - | 0 | Redis List (JSON job objects) |
| `myestro:global_settings` | Global settings cache | 3600s (1 soat) | 0 | Hash (key → JSON value) |
| `myestro:broadcast:queue` | Bot broadcast consumer queue | - | 1 | Redis List (BRPOP consumer) |
| Bot FSM (aiogram) | Conversation state | - | 1 | aiogram internal format |

### 6. API Endpoints (To'liq Reference)

#### 6.1. Auth (`/auth`)
| Endpoint | Method | Auth | Request Body | Response (200) | Xatoliklar |
|----------|--------|------|-------------|----------------|------------|
| `/auth/register` | POST | Yo'q | `{email, password, full_name, role, cefr_level, target_level, lang, auth_provider, provider_user_id, telegram_id}` | `{success, user}` | 409 email_already_registered, 409 phone_already_registered, 409 telegram_already_registered |
| `/auth/login` | POST | Yo'q | `{email, password}` | `{success, user}` | 401 invalid_email_or_password |
| `/auth/admin-login` | POST | Yo'q | `{email, password}` | `{success, user}` | 401 invalid_email_or_password, 403 admin_access_required |
| `/auth/otp/send` | POST | Yo'q | `{email}` | `{message: "OTP sent"}` | - |
| `/auth/otp/verify` | POST | Yo'q | `{email, code}` | `{message: "OTP verified"}` | 401 invalid_otp |
| `/auth/telegram` | POST | Yo'q | `{id, first_name, username, photo_url, auth_date, hash}` | `{success, user}` | 401 invalid_telegram_auth_data |
| `/auth/register-init` | POST | Yo'q | `{email, password, full_name, phone, telegram_id}` | `{success, user}` | 409 email_already_registered |
| `/auth/check-email` | GET | Yo'q | `?email=...` | `{exists, user}` | - |
| `/auth/check-phone` | POST | Yo'q | `{phone}` | `{exists, user}` | - |
| `/auth/phone-login` | POST | Yo'q | `{phone, telegram_id, password}` | `{success, user}` | 401 user_not_found |

#### 6.2. Users (`/users`)
| Endpoint | Method | Auth | Request Body | Response (200) | Xatoliklar |
|----------|--------|------|-------------|----------------|------------|
| `/users` | GET | Yo'q | `?skip=0&limit=50` | `{data: [UserResponse], total: int}` | - |
| `/users/{user_id}` | GET | Yo'q | - | `UserResponse` | 404 user_not_found |
| `/users/{user_id}/chats` | GET | Yo'q | - | `[ThreadResponse]` | - |
| `/users/{user_id}/ai-toggle` | PUT | Yo'q | `{ai_enabled: bool}` | `UserResponse` | 404 user_not_found |
| `/users/me` | PUT | Yo'q | `{full_name, email, phone, cefr_level, target_level, lang}` | `UserResponse` | 404 user_not_found |
| `/users/{user_id}` | PUT | Yo'q | `{full_name, cefr_level, target_level, lang, phone}` | `UserResponse` | 404 user_not_found |
| `/users/{user_id}` | DELETE | Yo'q | - | `{message: "User soft-deleted"}` | 404 user_not_found |
| `/users/{user_id}/activate` | PUT | Yo'q | - | `{message, user}` | 404 user_not_found |

#### 6.3. Content (`/content`)
| Endpoint | Method | Auth | Request Body | Response (200) | Xatoliklar |
|----------|--------|------|-------------|----------------|------------|
| `/content` | GET | Yo'q | `?content_type=&is_active=` | `[ContentItemResponse]` | - |
| `/content` | POST | Yo'q | Multipart: `title, description, content_type, file, is_active` | `ContentItemResponse` | 400 content_type_must_be_video_or_file, 400 bot_token_not_set, 400 telegram_api_error |
| `/content/{id}` | PUT | Yo'q | `ContentItemUpdate` (JSON) | `ContentItemResponse` | 404 not_found |
| `/content/{id}` | PATCH | Yo'q | Multipart: `title, description, file` | `ContentItemResponse` | 404 not_found, 400 telegram_api_error |
| `/content/{id}` | DELETE | Yo'q | - | `{message}` | 404 not_found |
| `/content/public` | GET | Yo'q | `?content_type=&limit=100&offset=0` | `[ContentItemResponse]` | - |
| `/content/{id}/set-telegram-file-id` | POST | Yo'q | `?telegram_file_id=...` | `ContentItemResponse` | 404 not_found |

#### 6.4. Broadcast (`/broadcast`)
| Endpoint | Method | Auth | Request Body | Response (200) | Xatoliklar |
|----------|--------|------|-------------|----------------|------------|
| `/broadcast/send` | POST | admin | `{title, content, message_type, file_id, target_all_users, target_user_ids}` | `{broadcast_id, total_users, status}` | 400 no_users_match, 500 failed_to_create |
| `/broadcast/status/{broadcast_id}` | GET | admin | - | `{broadcast_id, title, status, total, sent, failed, created_at}` | 404 not_found |
| `/broadcast/history` | GET | admin | `?limit=50` | `[dict]` | - |

#### 6.5. Inbox (`/inbox`)
| Endpoint | Method | Auth | Request Body | Response (200) | Xatoliklar |
|----------|--------|------|-------------|----------------|------------|
| `/inbox/messages` | GET | admin | `?status=&limit=50&offset=0` | `[InboxMessageResponse]` | - |
| `/inbox/messages/{id}` | GET | admin | - | `{message, history}` | 404 not_found |
| `/inbox/messages/{id}/reply` | POST | admin | `{reply}` | `{status, message_id, admin_id, timestamp}` | 404 not_found, 500 failed |
| `/inbox/messages/{id}/status` | PATCH | admin | `{status}` | `{status, message_id, new_status}` | 404 not_found |
| `/inbox/stats` | GET | admin | - | `{total, new, replied, closed, unread}` | - |

#### 6.6. Settings (`/settings`)
| Endpoint | Method | Auth | Request Body | Response (200) | Xatoliklar |
|----------|--------|------|-------------|----------------|------------|
| `/settings/ai` | GET | Yo'q | - | `SystemSettingResponse` | 404 not_found |
| `/settings/ai-public` | GET | Yo'q | - | `{value}` | - |
| `/settings/ai` | PUT | Yo'q | `{value: "true"\|"false"}` | `SystemSettingResponse` | 400 value_must_be_true_or_false, 404 not_found |
| `/settings/global` | GET | Yo'q | - | `Dict[str, dict]` | - |
| `/settings/global/{key}` | GET | Yo'q | - | `{value, description, updated_at}` | 404 not_found |
| `/settings/global/{key}` | PATCH | admin | `{value: "true"\|"false"}` | `{status, setting_key, old_value, new_value, timestamp}` | 400 invalid_key, 400 value_must_be_true_or_false, 404 not_found |

#### 6.7. Stats (`/stats`)
| Endpoint | Method | Auth | Request Body | Response (200) | Xatoliklar |
|----------|--------|------|-------------|----------------|------------|
| `/stats` | GET | Yo'q | - | `StatsResponse` | - |
| `/stats/activity` | GET | Yo'q | `?days=7` | `[ActivityPoint]` | - |
| `/stats/cefr` | GET | Yo'q | - | `CEFRDistribution` | - |

#### 6.8. Knowledge (`/knowledge`)
| Endpoint | Method | Auth | Request Body | Response (200) | Xatoliklar |
|----------|--------|------|-------------|----------------|------------|
| `/knowledge/categories` | GET | Yo'q | - | `[KnowledgeCategoryResponse]` | - |
| `/knowledge/docs` | GET | Yo'q | `?category_id=&cefr_level=` | `[KnowledgeDocResponse]` | - |

#### 6.9. AI Assistant (`/ai-assistant`)
| Endpoint | Method | Auth | Request Body | Response (200) | Xatoliklar |
|----------|--------|------|-------------|----------------|------------|
| `/ai-assistant/query` | GET | Yo'q | `?prompt=...` | `{response: str}` | - |
| `/ai-assistant/analyze-logs` | POST | Yo'q | - | `{analyzed, results}` | - |

#### 6.10. Admin (`/admin`)
| Endpoint | Method | Auth | Request Body | Response (200) | Xatoliklar |
|----------|--------|------|-------------|----------------|------------|
| `/admin/ai-chat` | POST | Yo'q | `{prompt, system_prompt}` | `{response: str}` | - |

#### 6.11. Sync (`/sync`) — Tokenless (Bot ↔ Backend)
| Endpoint | Method | Auth | Request Body | Response (200) | Xatoliklar |
|----------|--------|------|-------------|----------------|------------|
| `/sync/user/{telegram_id}` | GET | Yo'q | - | `UserResponse` | 404 not_found |
| `/sync/user` | POST | Yo'q | `{telegram_id, telegram_username, phone, full_name, cefr_level, lang, auth_provider, provider_user_id}` | `UserResponse` | 409 already_exists |
| `/sync/user/{telegram_id}` | PUT | Yo'q | `{full_name, email, phone, cefr_level, lang, password}` | `UserResponse` | 404 not_found |
| `/sync/users/{telegram_id}/ai-toggle` | PUT | Yo'q | `{ai_enabled}` | `{ai_enabled}` | 404 not_found |
| `/sync/reply/{user_id}` | POST | Yo'q | `{content, ai_model}` | `{status, message_id}` | - |
| `/sync/telegram-message` | POST | Yo'q | `{telegram_user_id, thread_id, role, content, content_type, ai_model, tokens_used, grammar_corrections, vocabulary_suggestions}` | `{status, message_id}` | - |
| `/sync/error` | POST | Yo'q | `{service, error_type, error_message, stack_trace, severity, metadata}` | `{status, error_id}` | - |
| `/sync/health` | GET | Yo'q | - | `{status, version}` | - |

#### 6.12. Bot Texts (`/bot-texts`)
| Endpoint | Method | Auth | Request Body | Response (200) | Xatoliklar |
|----------|--------|------|-------------|----------------|------------|
| `/bot-texts` | GET | Yo'q | `?key=&lang=` | `[BotTextResponse]` | - |
| `/bot-texts` | POST | Yo'q | `{key, lang, text}` | `BotTextResponse` | - |
| `/bot-texts/{id}` | PUT | Yo'q | `{text}` | `BotTextResponse` | 404 not_found |
| `/bot-texts/{id}` | DELETE | Yo'q | - | `{message}` | 404 not_found |

#### 6.13. Admin Messages (`/admin-messages`)
| Endpoint | Method | Auth | Request Body | Response (200) | Xatoliklar |
|----------|--------|------|-------------|----------------|------------|
| `/admin-messages` | GET | Yo'q | `?is_read=` | `[AdminMessageResponse]` | - |
| `/admin-messages` | POST | Yo'q | `{user_id, user_telegram_id, user_name, content_type, text, file_id}` | `AdminMessageResponse` | - |
| `/admin-messages/{id}/reply` | POST | Yo'q | `{reply}` | `AdminMessageResponse` | 404 not_found |
| `/admin-messages/{id}/read` | POST | Yo'q | - | `AdminMessageResponse` | 404 not_found |

#### 6.14. Exams (`/exams`) — Stub
| Endpoint | Method | Auth | Response |
|----------|--------|------|----------|
| `/exams/` | GET | Yo'q | `{exams: []}` |
| `/exams/{exam_id}` | GET | Yo'q | `{exam_id}` |

#### 6.15. Logs (`/logs`) — Admin Only
| Endpoint | Method | Auth | Request Body | Response (200) | Xatoliklar |
|----------|--------|------|-------------|----------------|------------|
| `/logs/` | GET | admin | `?level=&limit=100&offset=0&hours=24` | `[LogEntry]` | - |
| `/logs/search` | GET | admin | `?q=...&level=&limit=50` | `[LogEntry]` | - |
| `/logs/stats` | GET | admin | `?hours=24` | `{period_hours, total_logs, by_level, by_module, recent_errors}` | - |
| `/logs/user/{user_id}` | GET | admin | `?limit=50` | `[LogEntry]` | - |

#### 6.16. WebSocket (`/ws/admin`)
| Endpoint | Protocol | Auth | Description |
|----------|----------|------|-------------|
| `/ws/admin` | WebSocket | JWT token (first message) | Real-time error notifications (every 30s) |

#### 6.17. Request/Response JSON Example

**`POST /auth/admin-login` — Request:**
```json
{
  "email": "admin@myestro.com",
  "password": "admin123"
}
```

**Response (200):**
```json
{
  "success": true,
  "user": {
    "id": 1,
    "email": "admin@myestro.com",
    "full_name": "Super Admin",
    "role": "admin",
    "cefr_level": "C2",
    "target_level": "C2",
    "lang": "uz",
    "is_active": true,
    "is_verified": true,
    "profile_completed": true,
    "telegram_id": null,
    "telegram_username": null,
    "auth_provider": "email",
    "avatar_url": null,
    "phone": null,
    "ai_enabled": true,
    "last_login_at": null,
    "created_at": "2024-01-01T00:00:00"
  }
}
```

**`POST /broadcast/send` — Request:**
```json
{
  "title": "Yangi kurs boshlandi!",
  "content": "<b> Yangi kurs boshlandi! </b>",
  "message_type": "text",
  "file_id": null,
  "target_all_users": true,
  "target_user_ids": null
}
```

**Response (200):**
```json
{
  "broadcast_id": "550e8400-e29b-41d4-a716-446655440000",
  "total_users": 150,
  "status": "queued"
}
```

#### 6.18. Xatolik Kodlari
| HTTP Status | Error Code | Sabab |
|-------------|-----------|-------|
| 400 | `validation_error` | Input validatsiyadan o'tmadi |
| 400 | `bad_request` | Noto'g'ri so'rov (content_type, file, etc.) |
| 401 | `unauthorized` | Token/API-Key noto'g'ri yoki muddati o'tgan |
| 401 | `invalid_email_or_password` | Email yoki parol noto'g'ri |
| 401 | `invalid_otp` | OTP kod noto'g'ri |
| 401 | `invalid_telegram_auth_data` | Telegram hash noto'g'ri |
| 403 | `forbidden` | Huquq yetarli emas |
| 403 | `admin_access_required` | Admin roli talab etilmoqda |
| 404 | `not_found` | Resurs topilmadi |
| 409 | `conflict` | Resurs allaqachon mavjud (email/phone/telegram) |
| 429 | `rate_limit_exceeded` | So'rov limiti oshdi |
| 500 | `internal_error` | Server xatoligi |
| 500 | `failed_to_create_broadcast` | Broadcast yaratishda xato |
| 503 | `service_unavailable` | Xizmat mavjud emas |

### 7. Xavfsizlik

#### 7.1. Autentifikatsiya
| Mexanizm | Turi | Format | Hash/Algorithm | Muddati | Qayerda Ishlatiladi |
|----------|------|--------|---------------|---------|---------------------|
| API-Key | Header: `X-API-Key` | `sk-prefix-{64 hex chars}` | SHA-256 (storage), random (generation) | Per-key configurable | Client so'rovlari |
| JWT | Header: `Authorization: Bearer {token}` | `header.payload.signature` | HS256 | 15 min (access), 7 days (refresh) | Admin panel, WebSocket |
| Session | Cookie | `session_{uuid}` | Signed | Browser session | Web UI |
| Telegram Auth | POST body | `{id, first_name, username, auth_date, hash}` | HMAC-SHA256 (Telegram verify) | One-time | Bot registration |

**Eslatma:** Hozirda admin panel **tokenless** rejimda ishlaydi (localStorage da `isAdminLoggedIn` flag). JWT tokenlar yaratiladi lekin admin panel tomonidan ishlatilmaydi. Bu kelajakdagi faza uchun texnik qarz.

#### 7.2. Avtorizatsiya
| Rol | Ruxsat | Tavsifi |
|-----|--------|--------|
| `admin` | To'liq | Barcha operatsiyalar (broadcast, inbox, logs, settings) |
| `superadmin` | To'liq | Barcha operatsiyalar + admin yaratish |
| `student` | O'qish/Yozish | O'z profili, AI chat, imtihon topshirish |
| `readonly` | Faqat o'qish | GET endpoint'lari |

**Auth dependency chain:**
- `get_current_user` — JWT token orqali foydalanuvchi aniqlash
- `require_role(["admin", "superadmin"])` — `require_admin` aliasi
- `require_role(["superadmin"])` — `require_superadmin` aliasi
- Sync API (`/sync/*`) — hech qanday auth talab qilmaydi (tokenless)

#### 7.3. Himoya Choralari
| Himoya | Implementatsiya | Tavsifi |
|--------|----------------|--------|
| Rate Limiting | Redis INCR + EXPIRE | OTP rate limiting (300s TTL) |
| Parol Hash | bcrypt (12 rounds) | `hash_password()` / `verify_password()` |
| Input Validatsiya | Pydantic schema | Barcha API input'lari schema orqali |
| SQL Injection | SQLAlchemy ORM | Parametrized queries, hech qanday raw SQL |
| XSS | HTML parse_mode (Telegram) | Bot xabarlari HTML formatda, avtomatik escaping |
| CORS | Configurable origins | `ALLOWED_ORIGINS` env orqali allowlist |
| CSRF | Double-submit cookie | Admin panel uchun (hozirda tokenless) |
| Account Locking | 5 failed attempts → 15 min block | Auth service da implementatsiya (kelajakdagi faza) |
| Bot Guard | Global BOT_ENABLED toggle | Bot middleware orqali tekshiriladi |
| AI Guard | Global AI_ENABLED + user ai_enabled | Bot middleware orqali tekshiriladi |
| Channel Check | Telegram channel membership | Bot middleware orqali tekshiriladi |

### 8. UI/UX

#### 8.1. Sahifalar va Marshrutlar
| Sahifa | Marshrut | Ma'lumot Manbai | Auth Kerakmi |
|--------|----------|-----------------|-------------|
| Login | `/login` | `/auth/admin-login` | Yo'q |
| Dashboard | `/dashboard` | `/stats`, `/stats/activity`, `/stats/cefr` | Ha (localStorage) |
| Users | `/users` | `/users` (paginated) | Ha (localStorage) |
| Content | `/content` | `/content` (GET/POST), `/api/content` (proxy) | Ha (localStorage) |
| Broadcast | `/broadcast` | `/api/broadcast` (Next.js proxy) | Ha (localStorage) |
| Bot Texts | `#` | - | Yo'q (disabled) |
| Inbox | `#` | - | Yo'q (disabled) |
| Logs | `#` | - | Yo'q (disabled) |
| Settings | `#` | - | Yo'q (disabled) |
| AI Chat | `#` | - | Yo'q (disabled) |

#### 8.2. Komponentlar
| Komponent | Fayl | Props | State | API Calls |
|-----------|------|-------|-------|-----------|
| `Sidebar` | `components/layout/Sidebar.tsx` | - | - | `logout()` |
| `AuthGuard` | `components/AuthGuard.tsx` | `{children}` | `isLoggedIn`, `isLoading` | - |
| `StatsCard` | `components/dashboard/StatsCard.tsx` | `{icon, title, value, isLoading}` | - | - |
| `ActivityChart` | `components/dashboard/ActivityChart.tsx` | `{data, isLoading}` | - | - |
| `CEFRPieChart` | `components/dashboard/CEFRPieChart.tsx` | `{data, isLoading}` | - | - |
| `UserTable` | `components/users/UserTable.tsx` | `{users, isLoading, onView, onEdit, onDelete}` | - | - |
| `UserEditForm` | `components/users/UserEditForm.tsx` | `{user, onSave, isLoading}` | form state | `useUpdateUser` |
| `UserDetailModal` | `components/users/UserDetailModal.tsx` | `{user, isOpen, onClose}` | - | - |
| `ContentTable` | `components/content/ContentTable.tsx` | `{items, isLoading, onEdit, onDelete}` | - | - |
| `EditContentModal` | `components/content/EditContentModal.tsx` | `{item, isOpen, onClose, onSave, isLoading}` | form state | `useUpdateContent` |
| `LoginPage` | `app/login/page.tsx` | - | form state | `login()` |
| `DashboardPage` | `app/dashboard/page.tsx` | - | - | `useStats`, `useActivity`, `useCEFR` |
| `UsersPage` | `app/users/page.tsx` | - | page, search, selectedUser, editingUser, deletingUser | `useUsers`, `useUpdateUser`, `useDeleteUser` |
| `ContentPage` | `app/content/page.tsx` | - | title, description, contentType, file, editItem, deleteItem | `useContentList`, `useUpdateContent`, `useDeleteContent` |
| `BroadcastPage` | `app/broadcast/page.tsx` | - | message, mediaType, mediaUrl, userIdsRaw, broadcastId, progress | `fetch('/api/broadcast')` |

#### 8.3. Dizayn Tizimi
- **Ranglar:** Primary (`#F97316`), Primary hover (`#EA580C`), Dark (`#1C1917`), Sidebar (`#1C1917`)
- **Shriftlar:** Inter (default), sans-serif fallback
- **Spacing:** Tailwind CSS spacing system (p-4, m-2, gap-2, etc.)
- **Responsive:** `hidden md:block` (sidebar), `flex-col md:flex-row` (grid)
- **Dark/Light mode:** Yo'q (faqat light tema)
- **Animatsiyalar:** `animate-spin` (loading), `transition-colors` (hover), `transition-all` (progress bar)

### 9. Performance

| Metrika | Hozirgi Qiymat | Maqsad | Optimallashtirish |
|---------|----------------|--------|-------------------|
| API Response vaqti | ~50-200ms (local) | <100ms | Connection pooling, indexing |
| Bot AI javob vaqti | ~2-5s (OpenRouter) | <3s | Fallback models, token budgeting |
| Frontend bundle size | ~500KB (estimated) | <300KB | Code splitting, tree shaking |
| Database query vaqti | ~10-50ms | <20ms | Proper indexing, connection pooling |
| Broadcast send rate | ~25 msg/sec | ~50 msg/sec | Batch processing, rate limiting |
| Redis latency | <1ms | <1ms | Local Redis, connection pooling |

**Optimallashtirish:**
- Connection pooling (SQLAlchemy pool_size=10, max_overflow=20)
- Proper indexing (18+ indexes across tables)
- Redis caching (global settings, 1 hour TTL)
- AI fallback models (gemini → gpt-4o-mini → mistral)
- Telegram file_id caching (broadcast worker media cache)
- Frontend React Query (staleTime=30s, automatic refetch)

### 10. Monitoring va Metrikalar

| Metrika | Manba | Realizatsiya | Davriylik |
|---------|-------|--------------|-----------|
| API request count | Backend (FastAPI) | `api_logs` jadvali | Real-time |
| API response time | Backend (FastAPI) | `api_logs.response_time_ms` | Real-time |
| Error count | Backend (ErrorLog) | `error_logs` jadvali | Real-time |
| AI health | Backend (ai_service) | `health_check()` | Startup + manual |
| Bot health | Bot (main.py) | AI health check | Startup |
| User count | Backend (stats.py) | `/stats` endpoint | Real-time |
| Active users (7d) | Backend (stats.py) | `/stats` endpoint | Real-time |
| CEFR distribution | Backend (stats.py) | `/stats/cefr` endpoint | Real-time |
| Broadcast progress | Redis (progress hash) | `/broadcast/status/{id}` | Real-time |
| WebSocket errors | Backend (admin_ws.py) | WebSocket connection | Real-time |
| Log levels | Backend (logs.py) | `/logs/stats` | Real-time |

### 11. Known Issues

| # | Muammo | Ta'siri | Qaysi Phase'da Tuzatiladi | Urgentlik |
|---|--------|---------|--------------------------|-----------|
| 1 | Admin panel tokenless auth (localStorage) | XSS orqali sessiya o'tkazib yuborish riski | Phase 7 (Security hardening) | High |
| 2 | `/exams` endpoint'lari stub (return empty) | Imtihon funksiyasi ishlamaydi | Phase 8 (Exam system) | Medium |
| 3 | Bot broadcast listener o'chirilgan (`broadcast_listener` ishlatilmaydi) | Broadcast faqat backend queue'ga qo'shadi, bot eshitmaydi | Phase 3 (Broadcast) | Medium |
| 4 | `backend_users.py` root papkasida (duplikat `/users` router) | Ikki `/users` endpoint'lari — biri `list_users` funksiyasi bilan konflikt | Phase 1 (Cleanup) | Low |
| 5 | Admin panel `api.ts` da `baseURL: localhost:8000` (hardcoded) | Production'da noto'g'ri URL | Phase 1 (Config) | Low |
| 6 | `CHANNEL_ID` .env da yo'q | Channel check middleware avtomatik o'tkazib yuboradi | Phase 2 (Channel) | Low |
| 7 | `admin_messages` jadvali `admin_messages.py` da, lekin `inbox.py` da `InboxMessage` modeli ishlatiladi | Model/schema nomlari farq qiladi | Phase 4 (Inbox) | Medium |
| 8 | Frontend `types.ts` da `UserResponse` interfeysi ikki marta aniqlanadi | TypeScript duplicate interface xatosi | Phase 1 (Cleanup) | Low |
| 9 | `ai_assistant.py` da `analyze_logs` funksiyasi `log_id` ni `item.get("id")` orqali o'qiydapti, lekin `log_data` da `id` yo'q | AI log analysis ishlamaydi to'g'ri | Phase 5 (AI) | Low |
| 10 | Bot `MemoryStorage` ishlatiladi (Redis FSM yo'q) | Bot qayta ishga tushganda barcha FSM state yo'qoladi | Phase 2 (Bot) | Low |

### 12. Keyingi Bosqish (Phase)

**Joriy Phase:** Phase 6 (Structured Logging System) — `logs` jadvali yaratilgan, `/logs` API endpoint'lari ishga tushirilgan.

**Keyingi Phase:** Phase 7 (Security Hardening)
- JWT token admin panelga ulanishi
- CSRF protection qo'shish
- Account locking (5 failed attempts → 15 min block)
- Rate limiting (Redis INCR + EXPIRE)
- Input validation kengaytirish
- Security headers (HSTS, X-Frame-Options, etc.)

**Qolgan subtask'lar:**
- Phase 8: Exam system to'liq implementatsiyasi (`/exams` endpoint'lari)
- Phase 9: Bot broadcast listener qayta ishga tushirish
- Phase 10: Frontend `api.ts` baseURL konfiguratsiyasi
- Phase 11: `backend_users.py` duplikatini tozalash
- Phase 12: Frontend `types.ts` duplicate interface ni tozalash

### 13. Arxitekturaviy Qarorlar

| # | Qaror | Sabab | Alternativlar | Rad etilish Sababi |
|---|-------|-------|---------------|-------------------|
| 1 | FastAPI backend + aiogram bot (alohida jarima) | Telegram bot polling rejimda, backend REST API | Bitta async framework | aiogram faqat Telegram uchun, FastAPI REST uchun optimal |
| 2 | PostgreSQL + Redis (ikki xil DB) | PostgreSQL strukturirlangan ma'lumotlar uchun, Redis kesh/FSM/queue | Bitta PostgreSQL | Redis FSM va queue uchun optimal (aiogram RedisStorage) |
| 3 | SQLAlchemy 2.0 (sync + async) | Backend sync, bot async | Faqat async | Backend-da sync endpoint'lar ko'proq, oddiy |
| 4 | JWT (HS256) + bcrypt (12 rounds) | Oddiy, xavfsiz, sevimli | OAuth2, session-based | JWT stateless, bcrypt sevimli password hash |
| 5 | OpenRouter API (fallback models) | Bitta API orqali ko'p model | Direct API (OpenAI, Google) | OpenRouter bitta endpoint, fallback avtomatik |
| 6 | Docker Compose (4 service) | Oddiy, mahalliy ishga tushirish | Kubernetes | Mahalliyga mos, murakkablik kerak emas |
| 7 | Next.js 14 App Router | Yangi, server components, optimal | Pages Router | App Router yangi va optimal |
| 8 | Tailwind CSS | Tez development, konsistent dizayn | CSS Modules, Styled Components | Tailwind tezkor, class-based |
| 9 | Redis BRPOP (broadcast queue) | Bot faqat bitta consumer | Celery, RQ | Redis BRPOP oddiy, aiogram bilan mos |
| 10 | Telegram file_id (content storage) | Diskga saqlanmaydi, Telegram CDN | Local file storage | Telegram CDN tezkor, tekrar ishlatiladi |
| 11 | Pydantic schema validation | FastAPI bilan integratsiya | Marshmallow, dataclasses | Pydantic FastAPI default, optimal |
| 12 | aiogram MemoryStorage (FSM) | Oddiy, mahalliyga mos | RedisStorage | MemoryStorage oddiy, Redis keyinroq qo'shish mumkin |
| 13 | Tokenless sync API (`/sync/*`) | Bot backendga autentikatsiz kira olishi kerak | JWT bot tokeni | Bot backendga har doim ulanishi kerak, tokenless oddiy |
| 14 | HTML parse_mode (Telegram) | Bot xabarlari formatlash uchun | Markdown, plain text | HTML keng qo'llab-quvvatlanadi, xavfsiz |
| 15 | VARCHAR (ENUM sifatida) | PostgreSQL ENUM qo'shqa murakkablik | PostgreSQL ENUM | VARCHAR oddiy, migration da ozgina |

### 14. Changelog (Loyiha Ichidagi)

| Versiya | Sana | O'zgarishlar | Muallif |
|---------|------|--------------|---------|
| 1.0.0 | 2024-01-01 | Dastlabki versiya — FastAPI backend, aiogram bot, Next.js admin | Myestro Team |
| 1.1.0 | 2024-03-15 | Broadcast system (Phase 3) — `/broadcast` API, Redis queue, BroadcastWorker | Myestro Team |
| 1.2.0 | 2024-05-20 | Inbox system (Phase 4) — `/inbox` API, admin-user messaging | Myestro Team |
| 1.3.0 | 2024-07-10 | Global settings (Phase 5) — `/settings/global`, BotGuard, AIGuard middleware | Myestro Team |
| 1.4.0 | 2024-08-15 | Structured logging (Phase 6) — `/logs` API, `logs` jadvali, JSON formatter | Myestro Team |
| 1.5.0 | 2024-09-20 | Knowledge base — `/knowledge` API, `KnowledgeCategory`, `KnowledgeDoc` | Myestro Team |
| 1.6.0 | 2024-10-25 | Content management — `/content` API, Telegram file_id storage, admin upload | Myestro Team |
| 1.7.0 | 2024-11-30 | Bot texts CMS — `/bot-texts` API, i18n (uz, ru, en) | Myestro Team |
| 1.8.0 | 2025-01-15 | Admin panel — Next.js 14, dashboard, users, content, broadcast pages | Myestro Team |
| 1.9.0 | 2025-03-20 | WebSocket — `/ws/admin`, real-time error notifications | Myestro Team |
| 2.0.0 | 2025-06-20 | Repository yangilash — eski repo o'chirildi, yangi MyestroEcosystem repo yaratildi | Myestro Team |
| 2.1.0 | 2026-07-22 | Project-Overview yaratildi — to'liq arxitektura hujjatlari | Senior Developer |
