# Implementation Plan — Project-Overview.md Yangilash

## [Overview]

**Maqsad:** `C:/Users/HP/OneDrive/Documents/Cline/Rules/Project-Overview.md` faylini to'liq qayta yozish — hozirgi noto'g'ri (Next.js 15/Prisma/PostgreSQL 16) tavsif o'rniga loyihaning **HAQIQIY holatini** aks ettiruvchi yangi kontent yoziladi.

**Til:** O'zbek
**Sana:** 15.08.2026
**Uslub:** To'liq qayta yozish (full rewrite), mavjud struktura saqlanadi (Texnologiya Stack, Funksiyalar, Database Schema, UI/UX, Test Coverage, Known Issues, Keyingi Bosqich)

**Haqiqiy loyiha tavsifi:**
- **Myestro** — AI asosidagi ingliz tili o'rganish platformasi ekotizimi
- 3 ta asosiy xizmat: Telegram Bot (Python/aiogram), Backend API (Python/FastAPI), Admin Panel (Next.js 14)
- PostgreSQL 15 + Redis 7 (Docker Compose orqali)
- Deploy: Railway (railway.toml, Procfile, start.sh)

---

## [Types]

Bu task faqat bitta Markdown hujjatni qayta yozishni o'z ichiga oladi — kod turlari, interfeyslar yoki ma'lumotlar tuzilmalari yaratilmaydi/o'zgartirilmaydi.

---

## [Files]

### O'zgartiriladigan fayl:
| Fayl | Amal |
|------|------|
| `C:/Users/HP/OneDrive/Documents/Cline/Rules/Project-Overview.md` | To'liq qayta yozish (overwrite) |

### Ma'lumot manbai sifatida ishlatilgan fayllar (o'zgartirilmaydi):
| Fayl | Nima uchun muhim |
|------|------------------|
| `docker-compose.yml` | Xizmatlar, versiyalar (postgres 15-alpine, redis 7-alpine, portlar) |
| `telegram_bot/requirements.txt` | Python dependensiyalar (aiogram 3.30.0, FastAPI, SQLAlchemy, asyncpg, redis) |
| `admin/package.json` | Admin panel stack (Next.js 14.2.3, React 18.3.1, Tailwind 3.4.1, TS 5.3.3) |
| `migrations/init.sql` | 22+ jadval, default admin user |
| `telegram_bot/backend/app/main.py` | Backend versiya (v2.1.0), routerlar ro'yxati |
| `telegram_bot/bot/main.py` | Bot handlerlar ro'yxati, middleware'lar |
| `telegram_bot/backend/app/services/ai_memory_service.py` | AI Memory tizimi tavsifi |
| `telegram_bot/shared/ai_client.py` | OpenRouter AI integratsiyasi (GPT-4, Gemini, Claude, Mistral) |

---

## [Functions]

Yangi Project-Overview.md tarkibidagi bo'limlar:

1. **Sarlavha** — "Project Overview — Loyiha Holati" + sana (15.08.2026)
2. **Texnologiya Stack** — jadval:
   - Telegram Bot: Python 3.x, aiogram 3.30.0, SQLAlchemy 2.0 (async), Redis
   - Backend API: Python, FastAPI 2.1.0, Pydantic, JWT auth
   - Admin Panel: Next.js 14.2.3, React 18.3.1, TypeScript 5.3.3, Tailwind CSS 3.4.1
   - Database: PostgreSQL 15 (port 5433)
   - Cache/Queue: Redis 7 (port 6380)
   - AI: OpenRouter API (GPT-4, Gemini, Claude, Mistral)
   - Deploy: Railway, Docker Compose
3. **Funksiyalar (Hozirgi)** — bajarilgan funksiyalar belgilangan [x] bilan:
   - [x] Telegram bot orqali ro'yxatdan o'tish (FSM, OTP, Telegram hash)
   - [x] AI Teacher (OpenRouter, 3 tilda: uz/ru/en, kontekst xotira)
   - [x] AI Memory tizimi (Redis cache + PostgreSQL persist, sessiyalar)
   - [x] Profil boshqaruvi (CEFR daraja, til, ism)
   - [x] Admin panel (dashboard, foydalanuvchilar, kontent, broadcast, inbox, testlar)
   - [x] Inbox tizimi (foydalanuvchi ↔ admin xabarlar, Redis queue)
   - [x] Broadcast (ommaviy xabar yuborish, Redis queue, tarix)
   - [x] Kontent boshqaruvi (video/hujjat, Telegram kanalga yuklash)
   - [x] Imtihonlar (exams moduli)
   - [x] Referral tizimi
   - [x] Eslatmalar (reminders)
   - [x] Global sozlamalar (bot/AI yoqish-o'chirish)
   - [x] Loglar (api_logs, error_logs, audit_logs)
   - [x] i18n (uz/ru/en)
4. **Database Schema (Hozirgi)** — 22+ jadval ro'yxati:
   - users, sessions, conversation_threads, messages
   - knowledge_categories, knowledge_docs
   - api_logs, error_logs, audit_logs
   - system_settings, global_settings
   - content_items, bot_texts
   - admin_messages, inbox_messages, inbox_message_history
   - broadcast_jobs, broadcast_history
   - ai_memory_sessions, ai_memory_messages
   - exams (exam_sections, exam_questions, exam_attempts, exam_answers)
   - logs
5. **UI/UX Holati**:
   - Admin panel: Tailwind CSS, responsive sidebar, dashboard (statistika, grafiklar)
   - Telegram bot: reply/inline klaviaturalar, 3 til
   - Dark/Light mode: Admin panelda mavjud emas
6. **Test Coverage**:
   - Unit: telegram_bot/tests/ mavjud (pytest)
   - Integration: qisman
   - E2E: yo'q
7. **Known Issues**:
   - Imtihonlar moduli to'liq yakunlanmagan (stub holatda)
   - Dark/Light mode admin panelda yo'q
   - E2E testlar yozilmagan
8. **Keyingi Bosqich (Phase)**:
   - Phase 2: To'lov tizimi, imtihonlar modulini yakunlash, E2E testlar, mobil ilova
9. **Eski holat** — eski yozuv arxiv sifatida saqlanadi

---

## [Dependencies]

- Hech qanday yangi dependensiya o'rnatilmaydi
- Faqat Markdown fayl tahrirlanadi
- Tashqi xizmatlar talab qilinmaydi

---

## [Testing]

- **Manually verify:** Fayl ochilib, kontent to'g'ri ekanligi tekshiriladi
- **Format tekshiruvi:** Markdown jadvallar va ro'yxatlar to'g'ri render bo'lishi
- **Kod tekshiruvi talab qilinmaydi** (faqat hujjat o'zgaradi)

---

## [Implementation Order]

1. `C:/Users/HP/OneDrive/Documents/Cline/Rules/Project-Overview.md` faylini o'qish (hozirgi holatni tasdiqlash)
2. Yangi kontentni tayyorlash (yuqoridagi bo'limlar asosida)
3. Faylni `write_to_file` bilan to'liq qayta yozish
4. Natijani tekshirish (fayl mazmuni, format)
5. `attempt_completion` bilan yakunlash