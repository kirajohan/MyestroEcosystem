# Project Aim — Myestro Broadcast System

## Asosiy Maqsad

Myestro platformasida **broadcast tizimini to'g'rilash** — admin panel orqali yuborilgan xabarlar bot orqali foydalanuvchilarga yetkazib berilsin. Tizim admin (Next.js) → backend (FastAPI) → Redis queue → bot (aiogram) → Telegram API ketma-ketligida ishlasin.

## Komponentlar

| # | Komponent | Texnologiya | Roli |
|---|-----------|-------------|------|
| 1 | Admin Panel | Next.js 14 | Broadcast yuborish UI + progress kuzatish |
| 2 | Admin API Proxy | Next.js API Routes | Backend'ga proxy (auth header bilan) |
| 3 | Backend Broadcast API | FastAPI | Job yaratish, Redis queue, progress tracking |
| 4 | Redis Queue | Redis 7 (DB 0) | Broadcast job queue + progress hash |
| 5 | Bot Broadcast Worker | aiogram 3.x | Redis queue consumer, Telegram API'ga xabar yuborish |
| 6 | PostgreSQL | PostgreSQL 15 | broadcast_jobs, broadcast_history jadvallari |

## Arxitektura

### Umumiy Sxema

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  Admin Panel    │     │  Backend API     │     │  Redis Queue     │
│  (Next.js)      │     │  (FastAPI)       │     │  (DB 0)          │
│                  │     │                  │     │                  │
│  /broadcast     │────▶│  /broadcast/send │────▶│  lpush:queue     │
│  /broadcast/:id │◀────│  /broadcast/    │◀────│  hget:progress   │
│  (progress poll)│     │  status/:id      │     │                  │
└──────────────────┘     └──────────────────┘     └────────┬─────────┘
                                                           │
                                                     ┌─────▼─────┐
                                                     │  Bot      │
                                                     │  (aiogram)│
                                                     │  Worker   │
                                                     │  BRPOP    │
                                                     └─────┬─────┘
                                                           │
                                                     ┌─────▼─────┐
                                                     │Telegram   │
                                                     │API        │
                                                     │send_msg   │
                                                     └───────────┘
```

### Protokollar

| Manba → Maqsad | Protokol | Port | Tavsifi |
|----------------|----------|------|--------|
| Admin → Backend | HTTP/HTTPS | 8002 | API proxy (Next.js API route) |
| Backend → Redis | RESP | 6380 | Queue + progress (DB 0) |
| Bot → Redis | RESP | 6380 | Queue consumer (DB 0) |
| Bot → Telegram | HTTPS | 443 | send_message, send_photo, etc. |

### Ma'lumot Oqimi

**Broadcast Flow:**
```
Admin (Next.js) → /api/broadcast (POST)
  → Backend /broadcast/send (JWT auth)
    → BroadcastService.create_broadcast()
      → Redis hset(broadcast:{id}:progress)
      → Redis lpush(myestro:broadcast:queue)
        → Bot BroadcastWorker (BRPOP)
          → Telegram API (send_message/send_photo/etc)
            → Redis hincrby (progress update)
              → Admin (polling /api/broadcast/:id)
```

## Phase'lar

### Phase 1: Admin API Proxy + Schema Fix
**Maqsad:** Admin panel broadcast yuborishi va progress kuzatishi uchun API route'lari yaratilsin.
**Subtasks:**
1. `admin/app/api/broadcast/route.ts` yaratish (POST — admin formdan backend `/broadcast/send` ga proxy)
2. `admin/app/api/broadcast/[id]/route.ts` yaratish (GET — progress polling uchun)
3. Schema konvertatsiyasi: `message→content`, `mediaType→message_type`, `mediaUrl→file_id`, `userIds→target_user_ids`, `broadcastId→broadcast_id`
**Qabul mezoni:** Admin panel `/api/broadcast` va `/api/broadcast/:id` ga murojaat qiladi, backendga to'g'ri formatda so'rov yuboradi.
**Muddati:** 1 kun

### Phase 2: Redis DB + Listener Fix
**Maqsad:** Backend va bot bir xil Redis DB da ishlasin, va bot worker ishga tushsin.
**Subtasks:**
1. `docker-compose.yml` da bot uchun `REDIS_URL: redis://redis:6379/0` qilish
2. `bot/main.py` da `BroadcastWorker` ni instantiate qilish va `asyncio.create_task(worker.start())` qo'shish
3. Eski `broadcast_listener()` ni o'chirish
**Qabul mezoni:** Bot queue ni kuzatadi, backenddan job kelganda ishlaydi.
**Muddati:** 1 kun

### Phase 3: Backend Schema + User ID Fix
**Maqsad:** Backend worker bilan schema moslashsin, va foydalanuvchi ID lari to'g'ri bo'lsin.
**Subtasks:**
1. `BroadcastService.create_broadcast()` da `media_url` qo'shish (file_id o'rniga)
2. `batch_number` qo'shish yoki worker da ixtiyoriy qilish
3. `get_filtered_user_ids()` da `User.telegram_id` qaytarish
**Qabul mezoni:** Worker job ni to'g'ri o'qiydi, foydalanuvchilarga to'g'ri telegram_id bilan xabar yuboradi.
**Muddati:** 1 kun

### Phase 4: DB + Model + UI
**Maqsad:** Broadcast jadvallari database da bo'lsin, model bo'lsin, admin UI "barcha foydalanuvchilarga" funksiyasi bo'lsin.
**Subtasks:**
1. `init.sql` ga broadcast jadvallarini qo'shish
2. `models/__init__.py` ga broadcast modelini qo'shish
3. Admin UI "target all users" checkboxi
**Qabul mezoni:** Barcha komponentlar to'g'ri ishlaydi.
**Muddati:** 1 kun

## Cheklovlar

- Byudjet: $0 (ochiq manba)
- Jamoa: 1 kishi (Senior Developer)
- Vaqt: 4 kun
- Stack: Python 3.12, FastAPI, aiogram 3.x, Next.js 14, PostgreSQL 15, Redis 7
- Broadcast worker faqat bitta bo'lishi kerak (ikkinchi consumer yo'q)

## Muvaffaqiyat Mezonlari (KPI)

| Metrika | Maqsad (3-4 oy) | Maqsad (1 yil) |
|---------|-----------------|----------------|
| Broadcast delivery rate | >95% | >99% |
| Broadcast latency | <5s queue | <1s queue |
| Admin UI response | <2s | <500ms |
| Error rate | <1% | <0.1% |

## Xavfsizlik Talablari

- JWT auth orqali admin broadcast yuboradi
- Rate limiting (Telegram FloodWait handling)
- Input validation (Pydantic schema)
- User ID validation (telegram_id mavjudligini tekshirish)

## Performance Talablari

- Redis queue orqali batch processing
- Media file_id kesh (qayta yuklamaslik)
- SEND_INTERVAL_SECONDS = 0.04 (~25 msg/sec)
- Progress polling 2s interval

## Arxitekturaviy Talablar

- Backend DB 0, Bot DB 0 (bitta DB)
- Worker bitta bo'lishi kerak
- Schema: admin ↔ backend ↔ worker bir xil formatda
