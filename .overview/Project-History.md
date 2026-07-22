---

### 22/07/2026 — 19:30 — Broadcast tizimini tuzatish (REJA TUZILDI)

**Phase:** Phase 3 (Broadcast System)

**Holat:** REJA (Hali bajarilmagan)

**Tavsif:**
Broadcast tizimi 7 ta kritik xatolik tufayli ishlamaydi. Tizimni ishga tushirish uchun quyidagi o'zgarishlar kerak:
1. Admin API proxy route'lari yaratilishi
2. Redis DB raqamini tekislash (backend DB 0, bot DB 1 edi)
3. BroadcastWorker ni ishga tushirish (bot main.py)
4. Schema mismatchlarni tuzatish (admin↔backend↔worker)
5. Foydalanuvchi ID larini telegram_id ga o'zgartirish
6. Broadcast jadvallarini init.sql ga qo'shish
7. Broadcast modelini yaratish

---

### 22/07/2026 — 19:55 — Broadcast tizimini tuzatish

**Phase:** Phase 3 (Broadcast System)

**Holat:** BAJARILDI

**Tavsif:**
Broadcast tizimi 7 ta asosiy muammo bartaraf qilindi. Har bir muammo alohida tahlil qilindi va tuzatildi.

**Reja (oldindan tuzilgan):**
1. Phase 1: Admin API proxy + auth fix
2. Phase 2: Redis DB + listener fix
3. Phase 3: Backend schema + user ID fix
4. Phase 4: DB + model + UI

**Bajarilgan ishlar:**

### Phase 1: Admin API Proxy + Auth Fix
**Fayllar:**
- `telegram_bot/backend/app/schemas/user.py` — Yangilandi
- `telegram_bot/backend/app/services/auth_service.py` — Yangilandi
- `telegram_bot/backend/app/api/auth.py` — Yangilandi
- `admin/context/AuthContext.tsx` — Yangilandi
- `admin/app/api/broadcast/route.ts` — Yaratildi
- `admin/app/api/broadcast/[id]/route.ts` — Yaratildi
- `admin/app/broadcast/page.tsx` — Yangilandi

**Nima qilindi:**
- `AdminLoginResponse` schema'ga `access_token` maydoni qo'shildi
- `authenticate_admin()` JWT token yaratadigan qilindi
- `admin_login()` endpoint'da token response'ga qo'shildi
- `AuthContext` localStorage'da `admin_token` saqlaydigan qilindi
- `admin/app/api/broadcast/route.ts` — POST endpointi yaratildi. Admin form ma'lumotlarini backend `/broadcast/send` ga proxy qiladi. Schema konvertatsiyasi: `message→content`, `mediaType→message_type`, `mediaUrl→file_id`, `userIds→target_user_ids`, `broadcastId→broadcast_id`. JWT token forwarding.
- `admin/app/api/broadcast/[id]/route.ts` — GET endpointi yaratildi. Admin progress polling so'rovlarini backend `/broadcast/status/{id}` ga proxy qiladi. Response formatini admin kutilgan formatga o'zgartiradi.
- Broadcast page token forwarding qo'shildi: `Authorization: Bearer ${token}` headeri bilan.

### Phase 2: Redis DB + Listener Fix
**Fayllar:**
- `docker-compose.yml` — Yangilandi
- `telegram_bot/bot/main.py` — Yangilandi

**Nima qilindi:**
- Bot `REDIS_URL` DB 1 dan DB 0 ga o'zgartirildi (backend bilan bir xil)
- `BroadcastWorker` instantiate qilindi va `asyncio.create_task(worker.start())` bilan ishga tushirildi
- Eski `broadcast_listener()` importi olib tashlandi (worker yangi va professional)
- `redis.asyncio` Redis client yaratildi

### Phase 3: Backend Schema + User ID Fix
**Fayllar:**
- `telegram_bot/backend/app/api/broadcast.py` — Yangilandi

**Nima qilindi:**
- `get_filtered_user_ids()` da `User.id` o'rniga `User.telegram_id` qaytariladi — bu Telegram'ga to'g'ri xabar yuborish uchun kerak
- Worker bilan schema moslashtirildi: `content` (text emas), `message_type` (media_type emas), `media_url` (file_id o'rniga, qiymati bir xil)
- `batch_number: 1` qo'shildi (worker kutilgan maydon)

### Phase 4: DB + Model + UI
**Fayllar:**
- `telegram_bot/backend/app/models/broadcast.py` — Yaratildi
- `telegram_bot/backend/app/models/__init__.py` — Yangilandi
- `migrations/init.sql` — Yangilandi
- `admin/app/broadcast/page.tsx` — Yangilandi
- `admin/lib/broadcasttypes.ts` — Yangilandi

**Nima qilindi:**
- `BroadcastJob` va `BroadcastHistory` SQLAlchemy modellari yaratildi
- `models/__init__.py` ga broadcast modellari importi qo'shildi
- `init.sql` ga broadcast_jobs va broadcast_history jadvallari qo'shildi
- Admin UI "Barcha foydalanuvchilarga yuborish" checkboxi qo'shildi
- `BroadcastProgress` type'ga `"failed"` status qo'shildi

**Texnik tushuntirish (dasturchi tilida):**

Broadcast tizimining arxitekturasi to'g'ri edi — Backend FastAPI endpoint'lari, Redis queue, Bot worker, Admin UI — hammasi mantiqiy joylashtirilgan edi. Asosiy muammo integratsiyada edi:

1. **Admin API proxy muammosi:** Next.js API route'lari backend'ga proxy sifatida ishlatilgan (content uchun), lekin broadcast uchun yaratilmagan edi. Admin sahifasi `/api/broadcast` ga fetch qilgan, bu route esa mavjud emas edi. Yechim: content API route'lari patterniga o'xshab ikkita proxy route yaratildi — POST va GET.

2. **Auth muammosi:** Admin auth tokenless edi. `AdminLoginResponse` schema'sida `access_token` commentlangan edi. Backend `/auth/admin-login` endpoint'i hech qachon JWT token qaytarmagan. Broadcast endpoint'lari esa `require_admin` (JWT talab qiladi) bilan himoyalangan. Yechim: `authenticate_admin()` da `create_access_token()` chaqirildi, `AdminLoginResponse` ga `access_token` qo'shildi, va Admin Context'da token localStorage'da saqlanadigan qilindi.

3. **Redis DB raqam muammosi:** `docker-compose.yml` da backend `REDIS_URL: redis://redis:6379/0` (DB 0) bilan, bot esa `REDIS_URL: redis://redis:6379/1` (DB 1) bilan ishlagan. Backend DB 0 ga `lpush` qilgan, bot DB 1 dan `brpop` qilgan — hech qachon bir-biriga yetkazib bera olmagan. Yechim: botni DB 0 ga o'tkazish.

4. **Listener muammosi:** `bot/main.py` da broadcast listener commentlangan edi `# broadcast_task = asyncio.create_task(broadcast_listener(bot))`. Worker `BroadcastWorker` import qilingan lekin hech qachon instantiate qilinmagan. Yechim: `BroadcastWorker(bot, redis_client)` yaratildi va `asyncio.create_task(worker.start())` bilan ishga tushirildi.

5. **Schema mismatch muammolari:**
   - Admin↔Backend: `message` vs `content`, `mediaType` vs `message_type`, `mediaUrl` vs `file_id`, `userIds` vs `target_user_ids`, `broadcastId` vs `broadcast_id`
   - Backend↔Worker: `file_id` vs `media_url`, `batch_number` yo'q
   - Yechim: Schema konvertatsiyasi admin API proxy'sida amalga oshirildi, backend esa worker bilan moslashtirildi

6. **User ID muammosi:** `get_filtered_user_ids()` `User.id` (DB ID) qaytargan, lekin Telegram `chat_id` sifatida `telegram_id` kutilgan. Yechim: `select(User.telegram_id)` ga o'zgartirildi.

**O'zgarishlar:**
| Fayl | O'zgarish turi | Tavsifi |
|------|---------------|---------|
| `admin/app/api/broadcast/route.ts` | Yaratildi | POST — admin form → backend /broadcast/send proxy |
| `admin/app/api/broadcast/[id]/route.ts` | Yaratildi | GET — progress polling proxy |
| `admin/app/broadcast/page.tsx` | Yangilandi | Token forwarding + "barcha foydalanuvchilarga" checkbox |
| `admin/context/AuthContext.tsx` | Yangilandi | Token localStorage saqlash |
| `admin/lib/broadcasttypes.ts` | Yangilandi | BroadcastProgress ga "failed" status qo'shildi |
| `telegram_bot/backend/app/schemas/user.py` | Yangilandi | AdminLoginResponse ga access_token qo'shildi |
| `telegram_bot/backend/app/services/auth_service.py` | Yangilandi | authenticate_admin JWT token yaratadi |
| `telegram_bot/backend/app/api/auth.py` | Yangilandi | admin_login response token qo'shildi |
| `telegram_bot/backend/app/api/broadcast.py` | Yangilandi | telegram_id, media_url, batch_number |
| `telegram_bot/backend/app/models/broadcast.py` | Yaratildi | BroadcastJob va BroadcastHistory modellari |
| `telegram_bot/backend/app/models/__init__.py` | Yangilandi | Broadcast model importi |
| `telegram_bot/bot/main.py` | Yangilandi | BroadcastWorker ishga tushirildi |
| `docker-compose.yml` | Yangilandi | Bot REDIS_URL DB 0 ga o'zgartirildi |
| `migrations/init.sql` | Yangilandi | broadcast_jobs va broadcast_history jadvallari qo'shildi |

**Xatolar va ularni yechimi:**
- Muammo yo'q. Broadcast tizimi kod darajasida to'g'ri qurilgan edi, faqat integratsiya va konfiguratsiya xatolari bor edi.

**Arxitekturaviy qarorlar:**
1. **Worker tanlovi:** `BroadcastWorker` yangi, professional worker tanlandi (eski `broadcast_listener` o'rniga). Worker rate limiting (SEND_INTERVAL_SECONDS = 0.04), FloodWait handling, media file_id cache, progress tracking ga ega.
2. **Admin API proxy pattern:** Content API route'laridagi pattern (NEXT_PUBLIC_API_URL → BACKEND_INTERNAL_URL) broadcast uchun ham ishlatildi.
3. **Schema konvertatsiyasi:** Admin form → backend API konvertatsiyasi Next.js API route'da amalga oshirildi. Bu backend'ga to'g'ridan-to'g'ri o'zgarish kiritishdan qochadi.

**Performance ta'siri:**
- Broadcast worker 25 msg/sec tezlikda yuboradi (SEND_INTERVAL_SECONDS = 0.04)
- Media file_id cache orqali qayta yuklanmaydi
- Redis progress tracking har bir xabar yuborilgandan keyin hincrby qiladi

**Keyingi bosqich uchun eslatmalar:**
- `admin/app/api/contents/[id]/route.ts` da GET endpoint'ida "Broadcast progress endpoint not yet implemented" placeholderi bor — bu endi broadcast route'ida mavjud, contents route'idan olib tashlash mumkin
- Eski `migrations/broadcast_tables.sql` endi kerak emas, chunki `init.sql` ga qo'shilgan

**KPI ta'siri:**
- Broadcast delivery rate: target >95%
- Broadcast latency: target <5s queue → Redis BRPOP ishlatiladi, real-time
</write_to_file>
</｜｜DSML｜｜tool_calls>