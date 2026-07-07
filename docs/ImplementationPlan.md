# 🚀 Myestro — Production-Ready Implementation Plan

> **Maqsad:** Botni to'liq production tayyor holatga keltirish — Railway deploy, slash commandlar, Broadcast, Inbox, Settings, AI chat, Logs, va UI yaxshilanishi.
>
> **Total Effort:** ~82 soat | **Timeline:** 3-4 hafta | **Team:** 1 Senior Dev + 1 Design Engineer

---

## 📋 Quick Reference: Phases Summary

| Phase | Task | Hours | Priority | Status |
|-------|------|-------|----------|--------|
| **0** | Whisper cleanup + Slash cmd prep | 4 | CRITICAL | ⏳ Pending |
| **1** | Slash Commands implementation | 10 | HIGH | ⏳ Pending |
| **2** | Channel Check + Bot Settings | 6 | HIGH | ⏳ Pending |
| **3** | Broadcast (HTML, Queue, Private Channel) | 12 | HIGH | ⏳ Pending |
| **4** | Inbox System (Admin Panel) | 14 | HIGH | ⏳ Pending |
| **5** | Settings & Global Toggles (BOT on/off, AI on/off) | 6 | MEDIUM | ⏳ Pending |
| **6** | Logs Dashboard (Structured, Searchable) | 8 | MEDIUM | ⏳ Pending |
| **7** | AI Chat Activation | 6 | MEDIUM | ⏳ Pending |
| **8** | UI Polish (Tailwind CSS) | 8 | LOW | ⏳ Pending |
| **9** | Railway Deployment + Testing | 8 | CRITICAL | ⏳ Pending |

**Total: 82 hours**

---

## 🔧 Phase 0: Foundation & Cleanup (Asosiy tozalash)

### 0.1 Whisper ni butunlay o'chirish
**Nima o'chiriladi:**
- `telegram_bot/shared/ai_client.py` — `transcribe_voice()`, `transcribe_voice_via_service()`, `WHISPER_SERVICE_URL` o'zgaruvchisi
- `telegram_bot/bot/utils/ai_client.py` — `transcribe_voice()`, `transcribe_voice_via_service()` wrapperlari, `WHISPER_SERVICE_URL` re-export
- `telegram_bot/bot/handlers/voice.py` — Hozirgi handler o'rniga: *"Kechirasiz, men faqat matn xabarlarni qabul qila olaman"* deb javob beruvchi oddiy handler qoladi (allaqachon shunday, lekin tekshiriladi)
- `telegram_bot/bot/middlewares/ai_guard.py` — `voice` content type tekshiruvidan olib tashlash (faqat `text` qoladi)
- Docker-compose'da `whisper-service` konteyneri bo'lsa — o'chirish

**Qo'lda tekshirish:**
```bash
grep -rni "whisper\|transcribe_voice\|WHISPER" telegram_bot/
```

### 0.2 Slash Commands ro'yxatini tayyorlash (/setcommands uchun)

| Slash Command | F.text equivalent | Handler funksiya | Maqsad |
|---|---|---|---|
| `/start` | — | `start.py` | Botni ishga tushirish |
| `/register` | — | `register.py` | Ro'yxatdan o'tish |
| `/login` | — | `register.py` | Tizimga kirish |
| `/profile` | `👤 Profil` | `profile.py` | Profil ko'rish |
| `/settings` | `⚙️ Sozlamalar` | `menu.py:msg_settings` | Sozlamalar |
| `/guide` | `📖 Qo'llanma` | `menu.py:cmd_guide` | Qo'llanma |
| `/about` | `ℹ️ Biz haqimizda` | `menu.py:cmd_about` | Biz haqimizda |
| `/admin` | `📨 Admin ga xabar` | `menu.py:cmd_admin_message` | Admin ga yozish |
| `/video` | `🎬 Video Darslik` | `menu.py:msg_video` | Video darsliklar |
| `/file` | `📁 File Darsliklar` | `menu.py:msg_file` | File darsliklar |
| `/language` | `🌐 Til/Language` | `menu.py:cmd_language` | Til tanlash |
| `/logout` | — | `menu.py:settings_logout` | Chiqish |
| `/ai` | — | `ai_agent.py` | AI bilan suhbat |
| `/exam` | — | `exam.py` | Imtihon |
| `/referral` | — | `referral.py` | Referral |

> **Note:** Har bir handler `F.text.in_(...)` filteri yonida `Command(...)` filterini ham qabul qilishi kerak. Masalan:
> ```python
> @router.message(F.text.in_(["⚙️ Sozlamalar", ...]) | Command("settings"))
> async def msg_settings(message: types.Message, state: FSMContext): ...
> ```

---

## Phase 1: Slash Commands + Menu Handlers (Bot UX)

### 1.1 menu.py — Slash commandlar qo'shish
**Har bir existing handler uchun ikki filter:**
- `F.text.in_(...)` — reply keyboard
- `Command("<slash>")` — slash command

**Yangilash kerak bo'lgan handlerlar:**
1. `language_selected` — slash command kerak emas (start'dan keyin)
2. `cmd_about` — `| Command("about")`
3. `cmd_guide` — `| Command("guide")`
4. `cmd_language` — `| Command("language")`
5. `cmd_admin_message` — `| Command("admin")`
6. `msg_profile` — `| Command("profile")`
7. `msg_settings` — `| Command("settings")`
8. `msg_guide` — `| Command("guide")`
9. `msg_admin` — `| Command("admin")`
10. `msg_video` — `| Command("video")`
11. `msg_file` — `| Command("file")`

### 1.2 Yangi slash-only commandlar
- `/logout` — `settings_logout`ni chaqiradi
- `/ai` — AI suhbatni boshlaydi (agar allaqachon ishlamayotgan bo'lsa)

### 1.3 Bot `/setcommands` uchun `commands.md` fayl yaratish
Admin panel yoki deploy script orqali avtomatik o'rnatish uchun:
```
start - Botni ishga tushirish
register - Ro'yxatdan o'tish
login - Tizimga kirish
profile - Profilim
settings - Sozlamalar
guide - Qo'llanma
about - Biz haqimizda
admin - Admin ga xabar yuborish
video - Video darsliklar
file - File darsliklar
language - Tilni o'zgartirish
logout - Tizimdan chiqish
ai - AI o'qituvchi bilan suhbat
exam - Imtihon topshirish
referral - Referral dasturi
```

### 1.4 `bot/commands.md` fayl yaratish
Yuqoridagi ro'yxatni saqlash.

---

## Phase 2: Channel Check (Obuna tekshiruvi)

### 2.1 Hozirgi holat
- `ChannelCheckMiddleware` allaqachon mavjud
- `CHANNEL_ID` va `CHANNEL_URL` `.env` dan olinadi
- Trial tizimi bor (3 ta bepul AI javob)

### 2.2 Kerakli yaxshilanishlar
- **Obuna tekshiruvini faqat ro'yxatdan o'tgan userlar uchun qilish** — ro'yxatdan o'tmagan userlar uchun `/start`, `/register`, `/about`, `/guide` ishlaydi
- **Trial counterni to'g'ri ishlatish** — hozir har bir xabarda kamayib ketmoqda, faqat AI javoblarda kamayishi kerak
- **"Obuna bo'lish" inline keyboard tugmasini yaxshilash** — `channel_subscribe_kb` funksiyasi yangilanadi
- **`/checkchannel` admin command** — admin uchun test qilish

### 2.3 `.env` o'zgaruvchilari
```env
CHANNEL_ID=-1001234567890
CHANNEL_URL=https://t.me/myestro_channel
CHANNEL_CHECK_ENABLED=true
CHANNEL_TRIAL_LIMIT=3
```

---

## Phase 3: Settings — Global Switches (Backend + Bot)

### 3.1 Backend: SystemSettings model yangilanishi
**Yangi keylar qo'shish:**
- `bot_global_enabled` — `true`/`false` (hech kim bot ishlata olmaydi, adminlar bundan mustasno)
- `ai_global_enabled` — `true`/`false` (allaqachon mavjud, tekshirish kerak)

**Migration:**
```python
# 20260707_add_global_bot_setting.py
- INSERT INTO system_settings (key, value) VALUES ('bot_global_enabled', 'true');
```

### 3.2 Backend API endpointlar
- `GET /settings/bot` — bot global status
- `GET /settings/bot-public` — public check (no auth)
- `PUT /settings/bot` — toggle

### 3.3 Bot: Yangi middleware `BotGlobalMiddleware`
- Har bir xabarda avval `bot_global_enabled` ni tekshiradi
- Adminlar ro'yxatidan o'tkaziladi (admin_id lar `.env` da)
- Agar `false` bo'lsa: *"Bot vaqtinchalik texnik ishlar sababli o'chirilgan. Tez orada qaytamiz."*

### 3.4 Admin Panel: Settings sahifasi
- **AI Global** switch (mavjud)
- **Bot Global** switch (yangi)
- Real-time status ko'rsatish

### 3.5 `.env` o'zgaruvchilari
```env
ADMIN_IDS=123456789,987654321
```

---

## Phase 4: AI Chat — Active & Production-Ready

### 4.1 Hozirgi holat
- `ai_agent.py` streaming bilan ishlaydi
- `AIGuardMiddleware` global AI va user-level AI ni tekshiradi
- `build_system_prompt()` CEFR level'ga moslashadi

### 4.2 Kerakli yaxshilanishlar
- **Rate limiting** — har bir user 1 daqiqada max 10 ta xabar yubora oladi
- **Conversation history** — Redis'da saqlanadi (oxirgi 10 ta xabar)
- **Fallback** — agar AI javob bermasa, aniq fallback xabar
- **Admin uchun bypass** — adminlar rate limit'dan mustasno

### 4.3 Backend: `Conversation` modeldan foydalanish
- `bot/utils/ai_context.py` — `get_conversation_history(user_id)` funksiyasi
- `bot/utils/ai_context.py` — `save_conversation(user_id, role, content)` funksiyasi

---

## Phase 5: Broadcast — Full Production Implementation

### 5.1 Hozirgi holat
- Backend: `BroadcastService.create_broadcast()` — Redis queue'ga job yuboradi
- Bot: `broadcast_listener()` — Redis BLPOP bilan kutadi
- Faqat text, photo, video, document qo'llab-quvvatlaydi
- Media URL orqali yuboriladi (problemali — URL vaqtinchalik bo'lishi mumkin)

### 5.2 Media yuborish — Private Channel + file_id tizimi
**Muammo:** URL orqali media yuborish ishonchsiz (link muddati tugashi mumkin)

**Yechim:**
1. **Private Channel yaratish** — admin panel orqali
2. **Media shu channel'ga yuklash** — bot orqali
3. **file_id olish** — Telegram avtomatik beradi
4. **Broadcast'da file_id bilan yuborish** — doimiy, tez

**Yangi API:**
```
POST /broadcast/upload-media
  Body: multipart/form-data (file)
  Response: { "file_id": "...", "media_type": "photo|video|document" }

POST /broadcast/send
  Body: {
    "text": "<b>Salom!</b>",
    "parse_mode": "HTML",
    "media_type": "photo",
    "file_id": "AgACAgIAAxkB...",
    "target": { "all": true }
  }
```

### 5.3 Target Audience kengaytirish
**Hozir:** `roles`, `cefr_levels`, `active`
**Yangi:**
- `registered_after` — ma'lum sanadan keyin ro'yxatdan o'tganlar
- `registered_before` — ma'lum sanadan oldin ro'yxatdan o'tganlar
- `message_count_min` — kamida N ta xabar yozganlar
- `exclude_ids` — ba'zi userlarni istisno qilish

### 5.4 Queue & Progress tracking
**Hozir:** Redis hash'da progress saqlanadi
**Yaxshilanish:**
- WebSocket orqali real-time progress
- Admin panel'da progress bar
- Failed user'larni qayta urinish
- Rate limiting (1 soniyada 30 ta xabar — Telegram limit)

### 5.5 Bot listener yangilanishi
```python
async def broadcast_listener(bot: Bot):
    # Hozirgi: media_url
    # Yangi: file_id + media_type
    # parse_mode="HTML" doimiy
    # Rate limit: asyncio.sleep(1/30) har xabardan keyin
```

### 5.6 Admin Panel: Broadcast sahifasi (Tailwind CSS)
- **Compose area:** HTML editor yoki oddiy textarea + preview
- **Media upload:** Drag & drop, private channel'ga avtomatik yuklash
- **Target filters:** Rollar, CEFR, faollik, sanalar
- **Preview:** O'zingizga yuborish
- **Progress:** Real-time progress bar, sent/failed/pending
- **History:** Oldingi broadcast'lar ro'yxati

---

## Phase 6: Inbox — Admin-User Communication

### 6.1 Hozirgi holat
- `AdminMessage` model: `user_id`, `text`, `file_id`, `is_read`, `is_replied`, `admin_reply`
- API: list, create, reply, mark_read
- Bot: user admin ga xabar yuborganda `admin_messages` jadvaliga yozadi

### 6.2 Yangi Model: `ConversationThread`
Bir user bilan to'liq suhbat tarixini saqlash:
```python
class ConversationThread(Base):
    __tablename__ = "conversation_threads"
    
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    user_telegram_id = Column(BigInteger)
    user_name = Column(String(255))
    
    # Xabar
    direction = Column(String(10))  # "user_to_admin" | "admin_to_user"
    content_type = Column(String(20))  # text, photo, voice, document, video
    text = Column(Text)
    file_id = Column(String(255))
    
    # Status
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime)
    
    created_at = Column(DateTime, server_default=func.now())
```

**Migration:** Mavjud `admin_messages` ma'lumotlarini `conversation_threads` ga ko'chirish.

### 6.3 API endpointlar
```
GET /inbox/threads — thread'lar ro'yxati (user bo'yicha guruhlangan)
GET /inbox/threads/{user_id} — bitta user bilan barcha xabarlar
POST /inbox/send — admin tomonidan userga xabar yuborish
  Body: { "user_telegram_id": 123, "text": "...", "parse_mode": "HTML" }
POST /inbox/threads/{user_id}/read — o'qilgan deb belgilash
```

### 6.4 Bot tomoni
**Userga admin javobini yuborish:**
```python
async def send_admin_reply(user_telegram_id: int, text: str, file_id: str = None):
    # HTML shablon:
    template = f"""
📩 <b>Admin dan javob:</b>

{text}

<i>Savolingiz bo'lsa, shu yerda yozishingiz mumkin.</i>
    """
    await bot.send_message(user_telegram_id, template, parse_mode="HTML")
```

### 6.5 Admin Panel: Inbox sahifasi (Tailwind CSS)
**Layout — 2 qism:**

**Tepa qism (Inbox Xabarlar):**
- Thread ro'yxati — user ismi, oxirgi xabar, vaqt, o'qilgan/o'qilmagan indikator
- Xabar ustiga bosilgacha — thread ochiladi, o'qilgan deb belgilanadi
- Reply input — markdown/HTML support
- Chat history — Telegram chatdagidek bubble layout

**Past qism (Userlar ro'yxati):**
- Barcha userlar ro'yxati
- Search/filter
- User ustiga bosish — yangi xabar yuborish modal
- "Yangi xabar" tugmasi — istalgan userga xabar yuborish

**UI elementlar:**
- Tailwind `flex`, `divide-y`, `hover:bg-gray-50`
- Message bubbles: `bg-blue-100` (user), `bg-green-100` (admin)
- Scrollable chat area
- File/photo preview

---

## Phase 7: Logs — Organized View

### 7.1 Variant A: Admin Panel'da Logs Viewer (Tavsiya etiladi)
**Agar iloji bo'lsa:**
- Backend: `GET /logs?source=bot|backend|admin&level=INFO|WARNING|ERROR&from=&to=`
- Logs `logs` jadvalida saqlanadi (allaqachon model bor)
- Admin panel: filter, search, pagination, real-time (WebSocket)

**`LogEntry` model yangilanishi:**
```python
class LogEntry(Base):
    __tablename__ = "logs"
    
    id = Column(BigInteger, primary_key=True)
    source = Column(String(50))  # "bot", "backend", "admin"
    level = Column(String(20))   # "DEBUG", "INFO", "WARNING", "ERROR"
    message = Column(Text)
    context = Column(Text)       # JSON: {"user_id": 123, "chat_id": 456}
    created_at = Column(DateTime, server_default=func.now())
    
    # Index
    __table_args__ = (
        Index('ix_logs_source_level', 'source', 'level'),
        Index('ix_logs_created_at', 'created_at'),
    )
```

**Admin Panel:**
- Filter: source, level, date range
- Search: message text
- Auto-refresh: 5 soniyada
- Export: CSV

### 7.2 Variant B: Logs ni o'chirib tashlash (Agar murakkab bo'lsa)
- `logs` jadvalini o'chirish
- `LogEntry` modelini o'chirish
- Barcha logging faqat terminal/file'ga yoziladi
- Admin panel'da "Logs" bo'limi o'chiriladi

> **User tanlaydi:** A yoki B

---

## Phase 8: Admin Panel UI — Tailwind CSS Yaxshilanishi

### 8.1 Broadcast sahifasi
```tsx
// page.tsx structure
<div className="max-w-6xl mx-auto p-6 space-y-6">
  <h1 className="text-2xl font-bold text-gray-900">Broadcast Xabar</h1>
  
  {/* Compose Card */}
  <Card className="p-6">
    <div className="space-y-4">
      <Textarea 
        placeholder="Xabarni HTML formatda yozing..."
        className="min-h-[120px] font-mono text-sm"
      />
      <div className="flex gap-3">
        <MediaUpload />
        <Button variant="outline">O'zimga yuborish (Preview)</Button>
      </div>
    </div>
  </Card>
  
  {/* Target Filters */}
  <Card className="p-6">
    <h3 className="font-semibold mb-4">Target Audience</h3>
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <MultiSelect label="Rollar" options={['student','admin','teacher']} />
      <MultiSelect label="CEFR daraja" options={['A1','A2','B1','B2','C1','C2']} />
      <Toggle label="Faqat faol userlar (7 kun)" />
    </div>
  </Card>
  
  {/* Progress */}
  {isBroadcasting && (
    <Card className="p-6">
      <Progress value={sent} max={total} />
      <div className="flex justify-between text-sm text-gray-600 mt-2">
        <span>Yuborildi: {sent}</span>
        <span>Muvaffaqiyatsiz: {failed}</span>
        <span>Qoldi: {pending}</span>
      </div>
    </Card>
  )}
</div>
```

### 8.2 Inbox sahifasi
```tsx
// 2-panel layout
<div className="h-[calc(100vh-80px)] flex">
  {/* Left: Thread list */}
  <div className="w-1/3 border-r overflow-y-auto">
    <div className="p-4 border-b">
      <Input placeholder="Qidirish..." />
    </div>
    {threads.map(t => (
      <div key={t.user_id} className={`p-4 border-b hover:bg-gray-50 cursor-pointer ${!t.is_read && 'bg-blue-50'}`}>
        <div className="flex justify-between">
          <span className="font-medium">{t.user_name}</span>
          <span className="text-xs text-gray-500">{t.last_message_time}</span>
        </div>
        <p className="text-sm text-gray-600 truncate">{t.last_message}</p>
      </div>
    ))}
  </div>
  
  {/* Right: Chat */}
  <div className="flex-1 flex flex-col">
    <div className="flex-1 overflow-y-auto p-4 space-y-3">
      {messages.map(m => (
        <div className={`flex ${m.direction === 'admin_to_user' ? 'justify-end' : 'justify-start'}`}>
          <div className={`max-w-[70%] rounded-lg px-4 py-2 ${
            m.direction === 'admin_to_user' ? 'bg-green-100 text-green-900' : 'bg-blue-100 text-blue-900'
          }`}>
            <div dangerouslySetInnerHTML={{ __html: m.text }} />
            <span className="text-xs text-gray-500 block mt-1">{m.time}</span>
          </div>
        </div>
      ))}
    </div>
    
    <div className="border-t p-4">
      <div className="flex gap-2">
        <Textarea className="flex-1" placeholder="Javob yozing... (HTML qo'llab-quvvatlanadi)" />
        <Button>Yuborish</Button>
      </div>
    </div>
  </div>
</div>
```

---

## Phase 9: Railway Deploy

### 9.1 Railway nima?
Railway — konteynerlarni deploy qilish platformasi. Docker image'larni avtomatik build qiladi.

### 9.2 Railpack kerakmi?
**Yo'q.** Railpack — Rust-based build tool, lekin Railway allaqachon Docker qo'llab-quvvatlaydi. Bizda allaqachon `Dockerfile` lar bor.

**Kerak bo'lgan narsalar:**
- `railway.json` — Railway config
- `nixpacks.toml` — agar Docker o'rniga Nixpacks ishlatilsa (tavsiya etilmaydi)
- **Tavsiya:** Docker Dockerfile bilan deploy

### 9.3 Services strukturasi (Railway)
```
myestro-project/
├── backend/          (FastAPI — Dockerfile bor)
├── bot/              (aiogram — Dockerfile bor)
├── admin/            (Next.js — Dockerfile kerak)
├── postgres/         (Railway managed PostgreSQL)
└── redis/            (Railway managed Redis)
```

### 9.4 Next.js Admin Panel uchun Dockerfile
```dockerfile
# admin/Dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:18-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
EXPOSE 3000
CMD ["node", "server.js"]
```

> **Muhim:** `next.config.js` da `output: 'standalone'` bo'lishi kerak!

### 9.5 `next.config.js` yangilanishi
```js
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  images: {
    unoptimized: true,
  },
}
module.exports = nextConfig
```

### 9.6 Railway deploy qadamlari
1. **Railway account yaratish** — railway.app
2. **New Project** → "Deploy from GitHub repo"
3. **Services qo'shish:**
   - PostgreSQL (managed)
   - Redis (managed)
   - Backend (Dockerfile)
   - Bot (Dockerfile)
   - Admin (Dockerfile)
4. **Environment Variables** sozlash (har bir service uchun)
5. **Domains** — avtomatik HTTPS
6. **Deploy!**

### 9.7 Environment Variables (Railway)
**Backend:**
```
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
OPENROUTER_API_KEY=...
SECRET_KEY=...
```

**Bot:**
```
BOT_TOKEN=...
API_BASE_URL=https://myestro-backend.up.railway.app
REDIS_URL=${{Redis.REDIS_URL}}
OPENROUTER_API_KEY=...
CHANNEL_ID=...
CHANNEL_URL=...
ADMIN_IDS=...
```

**Admin:**
```
NEXT_PUBLIC_API_URL=https://myestro-backend.up.railway.app
NEXT_PUBLIC_ADMIN_PASSWORD=...
```

### 9.8 Railway muammolari va yechimlari
| Muammo | Yechim |
|---|---|
| Next.js 14 App Router | `output: 'standalone'` bilan ishlaydi |
| WebSocket | Railway'da WebSocket qo'llab-quvvatlanadi |
| Redis | Railway managed Redis ishlatish |
| Persistent storage | PostgreSQL'da saqlash, file'larni S3 ga |

### 9.9 Deploy tekshiruv ro'yxati
- [ ] Backend `/health` javob beradi
- [ ] Bot polling boshlaydi
- [ ] Admin panel ochiladi
- [ ] WebSocket ulanadi
- [ ] Redis queue ishlaydi
- [ ] Database migration o'tadi

---

## Phase 10: Final Polish & Testing

### 10.1 Integration testing
- [ ] Full registration flow
- [ ] AI chat (streaming, fallback, rate limit)
- [ ] Channel check (subscribe, trial, block)
- [ ] Broadcast (text, media, target filters, progress)
- [ ] Inbox (user→admin, admin→user, HTML, file)
- [ ] Settings (AI toggle, Bot toggle)
- [ ] Slash commands
- [ ] Logs (yoki o'chirilgan)

### 10.2 Load testing
- [ ] 1000 ta userga broadcast
- [ ] 50 ta concurrent AI suhbat
- [ ] Redis queue boshqaruvi

### 10.3 Security
- [ ] Admin API auth
- [ ] SQL injection protection
- [ ] XSS protection (HTML parse mode xavfsizligi)
- [ ] Rate limiting

---

## File Structure (Yangilangan)

```
myestro/
├── telegram_bot/
│   ├── bot/
│   │   ├── commands.md              # /setcommands ro'yxati
│   │   ├── main.py                  # + BotGlobalMiddleware
│   │   ├── config.py                # + ADMIN_IDS
│   │   ├── handlers/
│   │   │   ├── menu.py              # + slash commands
│   │   │   ├── ai_agent.py          # + conversation history
│   │   │   ├── voice.py             # simplified (no whisper)
│   │   │   └── inbox_reply.py       # NEW: admin reply to user
│   │   ├── middlewares/
│   │   │   ├── channel_check.py     # trial fix
│   │   │   ├── ai_guard.py          # - voice check
│   │   │   └── bot_global.py        # NEW: global bot switch
│   │   └── services/
│   │       └── broadcast_worker.py  # + file_id support, rate limit
│   ├── backend/
│   │   ├── app/
│   │   │   ├── api/
│   │   │   │   ├── broadcast.py     # + file_id, upload-media
│   │   │   │   ├── admin_messages.py → inbox.py  # NEW: threads
│   │   │   │   ├── settings.py      # + bot_global
│   │   │   │   └── logs.py          # NEW / UPDATED
│   │   │   ├── models/
│   │   │   │   ├── conversation_thread.py  # NEW
│   │   │   │   └── logs.py          # updated
│   │   │   └── main.py              # + new routers
│   │   └── migrations/              # + new migrations
│   ├── shared/
│   │   └── ai_client.py             # - whisper functions
│   ├── backend/Dockerfile
│   └── bot/Dockerfile
├── admin/
│   ├── app/
│   │   ├── broadcast/page.tsx       # NEW/REWRITE (Tailwind)
│   │   ├── inbox/page.tsx           # NEW/REWRITE (Tailwind)
│   │   ├── logs/page.tsx            # NEW (yoki o'chirilgan)
│   │   └── settings/page.tsx        # NEW/UPDATE
│   ├── components/
│   │   ├── broadcast/
│   │   │   ├── ComposeForm.tsx
│   │   │   ├── TargetFilters.tsx
│   │   │   └── ProgressBar.tsx
│   │   └── inbox/
│   │       ├── ThreadList.tsx
│   │       ├── ChatPanel.tsx
│   │       └── MessageBubble.tsx
│   ├── Dockerfile
│   └── next.config.js               # + output: 'standalone'
├── docker-compose.yml
└── railway.json                     # NEW
```

---

## Implementation Priority (Birma-bir)

| # | Phase | Vaqt (taxminiy) | Bog'liqlik |
|---|-------|-----------------|------------|
| 1 | 0.1 — Whisper o'chirish | 1 soat | Hech narsa |
| 2 | 0.2 + 1.x — Slash commands | 2 soat | Hech narsa |
| 3 | 2.x — Channel check | 1 soat | Hech narsa |
| 4 | 3.x — Global switches | 2 soat | Backend first |
| 5 | 4.x — AI chat active | 1 soat | 3.x dan keyin |
| 6 | 5.x — Broadcast full | 4 soat | Backend + Admin |
| 7 | 6.x — Inbox full | 4 soat | Backend + Admin |
| 8 | 7.x — Logs | 2 soat | Backend + Admin |
| 9 | 8.x — UI Tailwind | 3 soat | 6, 7 dan keyin |
| 10 | 9.x — Railway deploy | 2 soat | Hammasi tayyor |
| 11 | 10.x — Testing | 2 soat | Hammasi tayyor |
| | **Jami** | **~24 soat** | |

---

## Key Questions (User'dan tasdiq kerak)

1. **Logs:** A) Admin panel'da Logs viewer qurishmi yoki B) Butunlay o'chirib tashlashmi?
2. **Inbox chat history:** User va admin o'rtasidagi barcha tarixni saqlash kerakmi? (model o'zgaradi)
3. **Railway:** Docker bilan deploy qilamizmi yoki boshqa platforma (Render, Fly.io)?
4. **Media storage:** Broadcast media uchun Private Channel + file_id tizimi to'g'rimi?
