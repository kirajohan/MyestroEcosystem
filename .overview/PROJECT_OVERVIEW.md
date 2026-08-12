# Project Overview — Myestro Platform

---

## Hozirgi Holat — 2026-08-10

### Loyiha Haqida
**Myestro** — AI yordamida ingliz tilini o'rganish platformasi. Foydalanuvchilar Telegram bot orqali suhbatlashib, AI agent bilan ingliz tilini mashq qiladi, imtihonlar topshiradi, kontent o'rganadi va o'z progressini kuzatadi.

### Arxitektura (3 Servisli Tuzilma)

```
┌─────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   Admin Panel    │     │   Backend API     │     │   Telegram Bot    │
│   (Next.js 14)   │◄───►│   (FastAPI 0.115) │◄───►│   (aiogram 3.30)  │
│     :3000        │     │      :8000        │     │   (worker)        │
└─────────────────┘     └──────────────────┘     └──────────────────┘
         │                        │                       │
         └────────────┬───────────┴───────────┬───────────┘
                      │                       │
              ┌───────▼───────┐       ┌───────▼───────┐
              │   PostgreSQL  │       │     Redis     │
              │      :5432    │       │      :6379    │
              └───────────────┘       └───────────────┘
```

### Texnologiya Stack

| Qatlam | Texnologiya | Versiya |
|--------|-------------|---------|
| Telegram Bot | Python aiogram | 3.30.0 |
| Backend API | Python FastAPI + Uvicorn | 0.115.0 / 0.30.0 |
| Admin Panel | Next.js (App Router) | 14.2.3 |
| Frontend | React | 18.3.1 |
| Styling | Tailwind CSS | 3.4.1 |
| ORM | SQLAlchemy (asyncio) | 2.0.35 |
| Migrations | Alembic | 1.13.0 |
| Database | PostgreSQL | 15 (alpine) |
| Cache / Queue | Redis | 7 (alpine) |
| Auth | JWT (python-jose) + bcrypt | 3.3.0 / 4.2.0 |
| AI | OpenRouter API | — |
| HTTP Client | httpx | 0.27.0 |
| Validation | Pydantic | 2.9.0 |
| Scheduler | APScheduler | 3.10.4 |
| Deploy | Railway + Docker + docker-compose | latest |

### Servislar (docker-compose)

| Servis | Konteyner | Port (host) | Port (internal) |
|--------|-----------|-------------|-----------------|
| PostgreSQL | myestro-postgres | 5433 | 5432 |
| Redis | myestro-redis | 6380 | 6379 |
| Backend | myestro-backend | 8002 | 8000 |
| Bot | myestro-bot | — | — |
| Admin Panel | myestro-admin | 3002 | 3000 |

### Funksiyalar (Hozirgi Holat)

#### Telegram Bot (`telegram_bot/bot`)
- [x] Ro'yxatdan o'tish (FSM) — `handlers/register.py`
- [x] Profil boshqaruvi — `handlers/profile.py`
- [x] Asosiy menyu — `handlers/menu.py`
- [x] AI Chat (OpenRouter) — `handlers/ai_chat.py`
- [x] AI Agent — `handlers/ai_agent.py`
- [x] Akademiya (o'quv kontenti) — `handlers/academy.py`
- [x] Imtihonlar (exam) — `handlers/exam.py`
- [x] Eslatmalar (reminders) — `handlers/reminders.py`
- [x] Referral tizimi — `handlers/referral.py`
- [x] Admin panel (bot) — `handlers/admin.py`
- [x] Broadcast (ommaviy xabar) — `handlers/broadcast.py`
- [x] Inbox (admin bilan aloqa) — `handlers/inbox.py`
- [x] Media yuborish (voice/photo/video/document/sticker) — `handlers/voice.py`, `photo.py`, `video.py`, `document.py`, `sticker.py`
- [x] Aloqa (contact) — `handlers/contact.py`
- [x] Xatolarni boshqarish — `handlers/errors.py`

#### Backend API (`telegram_bot/backend`) — v2.1.0
- [x] Auth (register/login/refresh) — `api/auth.py`
- [x] Users CRUD — `api/users.py`
- [x] Content (video/file/text) — `api/content.py`
- [x] Exams (imtihonlar) — `api/exams.py`
- [x] AI Assistant — `api/ai_assistant.py`
- [x] Stats / Dashboard — `api/stats.py`
- [x] Broadcast — `api/broadcast.py`
- [x] Inbox (admin_messages) — `api/inbox.py`, `admin_messages.py`
- [x] Logs (api/error/audit) — `api/logs.py`
- [x] Settings — `api/settings.py`
- [x] Knowledge base — `api/knowledge.py`
- [x] Bot texts (CMS) — `api/bot_text.py`
- [x] Sync — `api/sync.py`
- [x] Admin — `api/admin.py`
- [x] WebSocket (admin realtime) — `websocket/admin_ws.py`

#### Admin Panel (`admin`)
- [x] Dashboard (stats + charts) — `app/dashboard/`
- [x] Foydalanuvchilar boshqaruvi — `app/users/`
- [x] Kontent boshqaruvi — `app/content/`
- [x] Broadcast yuborish — `app/broadcast/`
- [x] Inbox (xabarlar) — `app/inbox/`
- [x] Testlar — `app/tests/`
- [x] Login/Auth — `app/login/`
- [x] API routes (auth/broadcast/content/inbox/tests/users) — `app/api/`

### Database Schema (14+ jadval)

| Jadval | Tavsif |
|--------|--------|
| `users` | Foydalanuvchilar (role, cefr_level, telegram_id, ai_enabled) |
| `sessions` | JWT refresh sessionlar |
| `conversation_threads` | AI suhbatlar |
| `messages` | AI xabarlar (grammar_corrections, vocabulary_suggestions) |
| `knowledge_categories` | Bilim kategoriyalari |
| `knowledge_docs` | Bilim hujjatlari |
| `api_logs` | API loglar |
| `error_logs` | Xatolik loglari |
| `audit_logs` | Audit loglar |
| `system_settings` | Tizim sozlamalari |
| `content_items` | Video/File/Text darslar |
| `bot_texts` | Bot xabarlari CMS |
| `admin_messages` | Inbox (foydalanuvchi xabarlari) |
| `broadcast_jobs` | Broadcast vazifalari |
| `broadcast_history` | Broadcast tarixi |
| `exams` | Imtihonlar |
| `exam_sections` | Imtihon bo'limlari |
| `exam_questions` | Imtihon savollari |
| `exam_attempts` | Imtihon urinishlari |
| `exam_answers` | Imtihon javoblari |
| `ai_memory` | AI xotira tizimi |

### Middlewares (Bot)
- [x] `BotGuardMiddleware` — bot faolligini tekshiradi
- [x] `ChannelCheckMiddleware` — kanal obuna tekshiruvi
- [x] `AIGuardMiddleware` — AI global yoqilganligini tekshiradi

### AI Tizimi
- [x] OpenRouter API integratsiyasi — `utils/ai_client.py`
- [x] AI xotira tizimi — `utils/ai_memory_client.py`, `utils/ai_context.py`
- [x] AI promptlar — `utils/ai_prompts.py`, `ai_prompts_enhanced.py`
- [x] AI servis — `services/ai_service.py`
- [x] AI health check (startup da)

### Test Coverage

| Modul | Holat |
|-------|-------|
| Backend (FastAPI) | ✅ Mavjud — `test_auth`, `test_exams`, `test_security`, `test_stats`, `test_sync`, `test_users` |
| Telegram Bot | ❌ Yo'q |
| Admin Panel | ❌ Faqat `e2e.sh` skripti |

### Deploy Holati
- [x] Railway konfiguratsiyasi — `railway.toml` (3 servis + PostgreSQL + Redis)
- [x] Docker — `Dockerfile`, `docker-compose.yml`, admin/backend/bot Dockerfile'lar
- [x] Procfile — `worker: cd telegram_bot && python -m bot.main`
- [x] Herboku/start skript — `start.sh`
- [x] Migratsiya skriptlari — `scripts/migrate_db.py`, `scripts/deploy.sh`

### Known Issues
- Bot FSM storage: `MemoryStorage` ham `RedisStorage` ham yuklanadi, `dp` ikki marta `Dispatcher` bilan yaratiladi (kod ziddiyati — `main.py`'da ikkilangan `dp = Dispatcher(storage=...)`)
- Bot uchun testlar yozilmagan
- Admin panel uchun to'liq test coverage yo'q
- `telegram_bot/tests` bo'sh katalog
- Backend `requirements.txt`'da `psycopg2-binary` va `asyncpg` ikkalasi ham bor (ortiqcha)
- `migrations copy/` nomli zaxira katalogi kodda qolib ketgan

### Keyingi Bosqich (Next Phase)
- [ ] Bot uchun testlar yozish (pytest + pytest-asyncio)
- [ ] `main.py`'dagi Dispatcher ikkilanishini tozalash
- [ ] CI/CD pipeline qo'shish (GitHub Actions)
- [ ] Admin panel testlarini to'ldirish
- [ ] Ortiqcha fayllarni tozalash (`migrations copy/`, dublikat migrations)
- [ ] Safety: bot broadcast worker uchun monitoring

---

## ESKI — BOSHLANG'ICH HOLAT
[Loyiha Next.js + Prisma + NextAuth deb rejalashtirilgan edi, lekin haqiqiy loyiha Python (aiogram + FastAPI) + Next.js admin panel asosida qurilgan]

---

*Yaratildi: 2026-08-10*
*Oxirgi yangilanish: 2026-08-10*