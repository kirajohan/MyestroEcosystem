# Myestro — AI-Powered English Learning Platform

## Architecture

Myestro consists of 5 components:
1. **Telegram Bot** (aiogram 3.x) — User interface
2. **Backend API** (FastAPI) — Central hub
3. **Admin Panel** (Next.js 14) — Management UI
4. **Database** (PostgreSQL 15 + Redis 7)
5. **AI Engine** (OpenRouter — Gemini/GPT/Mistral)

## Quick Start
Git buyruqlari haqida tushuntirish:

## 1. Asosiy branchga o'tish (main branch)
```bash
git checkout main
```
Yoki yangi Git versiyalarida:
```bash
git switch main
```

Agar main nomi `master` bo'lsa:
```bash
git checkout master
```

## 2. O'zgarishlarni qo'shish va commit qilish
```bash
# Hammasini qo'shish
git add .

# Yoki ma'lum fayllarni qo'shish
git add papka/fayl.py

# Commit qilish
git commit -m "O'zgarishlar haqida izoh"
```

## 3. Push qilish (GitHub ga yuklash)
```bash
git push origin main
```

Agar birinchi marta push qilsangiz:
```bash
git push -u origin main
```

## To'liq misol (barchasini birgalikda):
```bash
git add .
git commit -m "Yangi funksiya qo'shildi"
git push origin main
```

Bu buyruqlarni loyiha papkasida terminalda ishga tushirishingiz kerak. Bundan oldin Git o'rnatilganligiga va loyiha allaqachon Git repozitoriyasi bo'lishiga ishonch hosil qiling.

Agar siz Git bilan tanish bo'lmasangiz va to'liq qo'llanma kerak bo'lsa, menga ayting, batafsilroq ma'lumot beraman.




```bash
# 1. Start infrastructure
docker compose up -d postgres redis

# 2. Start Backend
cd telegram_bot/backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 3. Start Bot
cd telegram_bot/bot
pip install -r requirements.txt
python -m bot.main

# 4. Start Admin Panel
cd app
npm install
npm run dev
```

## Docker Compose (full stack)

```bash
docker compose up --build
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| PostgreSQL | 5433 | Main database |
| Redis | 6380 | Cache + FSM |
| Backend API | 8002 | REST API + WebSocket |
| Admin Panel | 3002 | Next.js admin UI |

## Project Structure

```
c:\Projects\Myestro\
├── docker-compose.yml
├── migrations/       # init.sql, seed.sql
├── telegram_bot/
│   ├── backend/      # FastAPI (models, API, services)
│   └── bot/          # aiogram 3.x (handlers, KB, utils)
├── app/              # Next.js 14 Admin Panel
└── scripts/          # Deployment scripts
```

## Tech Stack

- **Backend**: Python 3.12, FastAPI, SQLAlchemy 2.0, psycopg2, JWT
- **Bot**: Python 3.12, aiogram 3.x, asyncpg, RedisStorage
- **Admin**: Next.js 14, TypeScript, Zustand, Recharts, Tailwind CSS
- **Database**: PostgreSQL 15, Redis 7
- **AI**: OpenRouter API (gemini → gpt-4o-mini → mistral)

*Hozirgi holatni saqlab qolgan holda , Barcha git repositorydan chiqip ket , va yangi Repository qur noldan , eski va hozirgisidan chiqip ket, ular kerak emas . 