# 🎓 Myestro Eco — AI asosidagi ingliz tilini o'rganish platformasi

**Myestro Eco** — Telegram bot, so'rov (backend) API va web admin panel orqali ishlaydigan
AI quvvatli ingliz tili o'rganish ekotizim tizimi. Foydalanuvchilar Telegram orqali ro'yxatdan
o'tadi, kanalga obuna bo'ladi va AI-suhbat, test/kviz, trening (academy), inbox xabarlari hamda
kontent bilan ishlaydi. Barcha jarayonlar Next.js asosidagi admin panel orqali boshqariladi.

---
MyestroEco/
├── .github/workflows/deploy.yml       # CI/CD (SSH deploy + alembic upgrade)
├── .vscode/settings.json
├── .env.example                       # (yangi) — template, sekretsiz
├── .env                               # sekretlar (gitignore'da)
├── .gitignore
├── docker-compose.yml                 # 6 servis: postgres, redis, backend, bot, admin, exam
├── README.md                          # umumiy obzor (yangilanadi)
├── PROJECT_STRUCTURE.md               # (yangi) — shu struttura hujjati
│
├── admin/                             # Next.js 14 — Admin Panel
│   ├── app/
│   │   ├── api/                       #   proksi-routes (18 ta)
│   │   ├── login/  dashboard/  users/  broadcast/  bot-texts/
│   │   │   content/  inbox/  tests/  exam/
│   │   ├── layout.tsx  page.tsx  globals.css
│   ├── components/                    #   UI + feature (broadcast, tests, users, ...)
│   ├── context/  hooks/  lib/  providers/  types/
│   └── Dockerfile  package.json  tsconfig.json  ...
│
├── exam/                              # Next.js — Landing + Exam
│   ├── app/
│   │   ├── (landing)/                 #   page.tsx (Aurora, Sections, Footer)
│   │   ├── login/  cabinet/  exams/
│   │   │   └── [attemptId]/  results/[attemptId]/
│   │   ├── layout.tsx  globals.css  providers.tsx
│   ├── components/                    #   AudioPlayer + landing/*
│   ├── lib/  public/
│   ├── middleware.ts  next.config.js  ...
│   └── README.md                      # (yangi)
│
├── telegram_bot/                      # Python monorepo
│   ├── backend/                       #   FastAPI REST API (2.1.0)
│   │   ├── app/
│   │   │   ├── api/                   #     auth, users, content, stats, exam_v2, ...
│   │   │   ├── core/                  #     security, deps, exceptions, session_deps
│   │   │   ├── models/  schemas/  services/  websocket/
│   │   ├── migrations/                #   Alembic (versions/, env.py)
│   │   ├── scripts/                   #   admin, seed, migrate skriptlar
│   │   └── alembic.ini  Dockerfile  requirements.txt
│   ├── bot/                           #   aiogram bot
│   │   ├── handlers/  keyboards/  middlewares/  services/
│   │   ├── states/  utils/  workers/
│   │   └── main.py  config.py  database.py  Dockerfile
│   ├── shared/                        #   ai_client, json_logger
│   ├── knowledge/                     #   RAG — 7 ta .md fayl + _index.yaml
│   └── requirements.txt
│
├── migrations/                        # SQL sxema
│   ├── init.sql                       #   20+ jadval + default admin
│   ├── versions/                      #   000–007 + ...
│   └── run_migrations.sh / .bat / README.md
│
└── scripts/                           # root-level util skriptlar
    └── migrate_sql.py


## 🧱 Texnologik stack

| Qatlam | Texnologiya |
|--------|-------------|
| **Backend** | Python 3.12, FastAPI 0.115, Uvicorn, SQLAlchemy 2.0 (async) |
| **Bot** | Python, aiogram 3.30, FSM (Redis storage) |
| **DB** | PostgreSQL 15 (asyncpg + psycopg2), Alembic migratsiyalar |
| **Cache/Queue** | Redis 7 (session, OTP, rate-limit, broadcast queue) |
| **AI** | OpenRouter API (Qwen), suhbat xottirasi (memory) |
| **Admin** | Next.js 14, TypeScript, Tailwind + shadcn/ui |
| **Admin libs** | TanStack React Query, React Hook Form + Zod, Recharts, Sonner |
| **Deploy** | Docker Compose, GitHub Actions (SSH), Railway/Heroku-ready |

## 🔌 Backend (FastAPI) — `telegram_bot/backend`

- **Versiya:** `2.1.0`, health endpoint `/health`
- **Async** SQLAlchemy + **asyncpg**, parallel Redis (OTP / rate-limit / cache)
- **JWT** auth — access (15 daqiqa) + refresh (7 kun) tokenlar
- **Routers:** `auth, users, content, stats, admin, ai_assistant, sync, knowledge,
  settings, bot_text, admin_messages, broadcast, inbox, logs, tests` + `websocket (admin_ws)`
- **Ichki servis (port 8001):** `/internal/refresh-cache` — bot matnlari cache-rini yangilaydi
- **Models:** user, session, conversation, broadcast (job/history), ai_memory, tests, bot_text,
  content, inbox, knowledge, logs, settings, admin_message

## 🤖 Telegram Bot (aiogram 3) — `telegram_bot/bot`

- Kirish nuqtasi: `python -m bot.main`
- **Middleware:** DbSession, BotGuard, ChannelCheck (kanal obunasi), AIGuard
- **Handler'lar:** start, register, profile, menu, test_quiz, inbox, ai_agent, voice,
  reminders, referral, academy, admin, photo, document, sticker, video, broadcast, contact, errors
- **Services:** AI (OpenRouter streaming), broadcast_worker, content_uploader
- **Workers:** inbox_delivery (fon, asyncio task)
- **AI:** OpenRouter orqali javob + suhbat kontekst xottirasi + ai_memory istoriyasi
- **Admin ID'lar:** `ADMIN_IDS` muhit o'zgaruvchisida (vergul bilan ajratilgan)

---

## 🖥️ Admin Panel (Next.js 14) — `admin/`

Barcha API so'rovlari Next.js API routes (`app/api/*/route.ts`) orqali backend API'ga proxy qilinadi.

- **Sahifalar:** `/dashboard`, `/users`, `/broadcast`, `/bot-texts`, `/tests`, `/content`, `/inbox`, `/login`
- **Proxy routes:** auth/login, bot-texts (+keys, +stats, [id]), broadcast (+history, placeholders,
  upload, [id]), content/contents, inbox/messages, tests (+[id]/questions/[qid]), users
- **Komponentlar:** AuthGuard, StatsCard, ActivityChart, CEFRPieChart, broadcast (AudienceSelector, MediaUploader)
- **Auth:** localStorage token, AuthContext, AuthGuard; **UI:** Tailwind + shadcn/ui + orange tema, dark sidebar

---

## 🗄️ Ma'lumotlar bazasi — `migrations/init.sql`

`users`, `sessions`, `conversation_threads`, `messages`, `broadcast_jobs`, `broadcast_history`,
`ai_memory_sessions`, `ai_memory_messages`, test/kviz jadvallari, `bot_texts`, `content`, `inbox`,
`knowledge`, `logs`, `settings`, `admin_messages` (20+ jadval).

Default admin tayanch bilan yaratiladi (init.sql ichida, `ON CONFLICT (email) DO NOTHING`).

---

## 🐳 Ishga tushurish (Docker Compose)

```bash
# 1. Muhit o'zgaruvchilarini sozlang
cp .env.example .env   # agar mavjud bo'lsa, aks holda .env dan foydalaning

# 2. Barcha servislarni qurish va ko'tarish
docker compose up --build

# 3. Migratsiyani qo'llash
docker compose exec -T backend alembic upgrade head
```

| Servis | Ichki port | Tashqi port |
|--------|-----------|-------------|
| postgres | 5432 | 5433 |
| redis | 6379 | 6380 |
| backend | 8000 | 8002 |
| bot | — (polling) | — |
| admin | 3000 | 3002 |

- Admin panel: `http://localhost:3002`
- API Swagger UI: `http://localhost:8002/docs`

---

## 🚀 CI/CD

`.github/workflows/deploy.yml` — `main` branchga push bo'lganda GitHub Actions:
1. SSH orqali serverga (secret'lardan: `DEPLOY_HOST`, `DEPLOY_USER`, `DEPLOY_KEY`)
2. `/opt/myestro` da `git pull origin main`
3. `docker compose build` + `up -d`
4. `alembic upgrade head` (migratsiya)

---

## 📝 Ish holati (Status)

- ✅ Auth / registration / JWT
- ✅ AI suhbat + memory + OpenRouter streaming
- ✅ Broadcast tizimi (Phase 1–4, history + upload + placeholders)
- ✅ Test/kviz tizimi (savollar, kanal savollari)
- ✅ Inbox / admin xabarlashuv / WebSocket
- ✅ Bot matnlar (bot-texts) + statistika
- ✅ Statistika, admin dashboard
- 🚧 Deploy va xavfsizlik sinxronlashtirish

---

## ⚠️ E'tiborga olingan holda

- `.env` tarkibida **haqiqiy secret-lar** (BOT_TOKEN, OPENROUTER_API_KEY, JWT secret-lar) mavjud —
  ular git history'da saqlanishi mumkin; production uchun ularni aylantirish (rotate) tavsiya etiladi.
- Kodda **`content.router` ikki marotaba** `include_router` (backend/app/main.py, qator 107 va 114).
- `telegram_bot/backend/migrations copy/` — keraksiz dublikat papka.
- Root README (ushbu fayl) — project overview sifatida yangilandi.

---

## 📜 Litsenziya

© 2026 Myestro Eco.
