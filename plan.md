Xo'p, do'stim! Qabul qilindi. **Step 1** ga o'tamiz. 

Bizning birinchi qadamimiz — barcha kelishuvlarimizni, arxitekturani va ishlash mantig'ini rasmiy hujjatga, ya'ni **`MAESTRO_EXAM_PLAN.md`** fayliga aylantirish. Bu hujjat bizning "yo'l xaritamiz" (roadmap) bo'ladi va butun jamoa (yoki kelajakdagi o'zingiz) uchun yagona haqiqat manbai (single source of truth) hisoblanadi.

Men hozirgi `PROJECT_OVERVIEW.md` va `Project-Overview.md` dagi ma'lumotlarga (ayniqsa, joriy stack, Docker tuzilmasi va auth mexanizmiga) tayanib, to'liq reja hujjatini tayyorladim.

Quyida `MAESTRO_EXAM_PLAN.md` fayli uchun tayyor kontent keltirilgan. Uni loyihaning root papkasiga saqlashimiz mumkin.

---

# 📄 MAESTRO_EXAM_PLAN.md

## 1. Maqsad va Konsepsiya
**Maestro Exam** — bu Myestro ekotizimi ichidagi mustaqil, lekin to'liq sinxron ishlaydigan veb-ilova (Web App). U foydalanuvchilarga ingliz tilini 4 ta asosiy ko'nikma (Listening, Reading, Writing, Speaking) bo'yicha imtihon topshirish imkonini beradi.
* **Arxitektura:** Alohida Frontend (Next.js), lekin umumiy Backend (FastAPI), umumiy Ma'lumotlar bazasi (PostgreSQL) va umumiy Auth tizimi (JWT + Telegram ID).
* **Asosiy qoida:** Eski `exam_*` jadvallari va kodi to'liq o'chiriladi. Yangi modul noldan, toza va kengaytiriladigan (scalable) qilib quriladi.

## 2. Rollar
1. **Foydalanuvchi (Student):** Telegram orqali tizimga kiradi, imtihon tanlaydi, topshiradi va AI dan tahliliy natija oladi.
2. **Administrator:** Joriy Admin Panel orqali imtihonlar, bloklar, savollar, audio fayllar va AI rubrikalarini boshqaradi.

## 3. Foydalanuvchi Stsenariylari (User Scenarios)
1. **Kirish (Login):** Foydalanuvchi Maestro Exam veb-saytiga kiradi -> "Login with Telegram" tugmasini bosadi -> Backend Telegram hash'ni tekshiradi -> JWT token beradi.
2. **Kabinet (Dashboard):** 5 ta asosiy bo'lim ko'rinadi (Full Exam, Listening, Reading, Writing, Speaking).
3. **Imtihon jarayoni:**
   * Foydalanuvchi imtihonni boshlaydi (`exam_attempts` yaratiladi).
   * Server taymer va deadline'ni nazorat qiladi.
   * Listening/Reading uchun avtomatik tekshiruv.
   * Writing/Speaking uchun media yuklash va AI navbatga qo'yish.
4. **Natija (Results):** Ball, CEFR darajasi, AI tahlili (xatolar, tavsiyalar, transkript).

## 4. Ma'lumotlar Bazasi Sxemasi (Yangi DB Schema)
Eski jadvallar (`exams`, `exam_sections`, `exam_questions`, `exam_attempts`, `exam_answers`) o'chiriladi. O'rniga quyidagi 10 ta yangi jadval yaratiladi:

| Jadval Nomi | Vazifasi |
| :--- | :--- |
| `exams` | Imtihonning o'zi (title, type, cefr_level, time_limit) |
| `exam_blocks` | Imtihon ichidagi modullar (masalan, Listening Part 1) |
| `exam_items` | Aniq savollar yoki topshiriqlar (audio_url, passage_text) |
| `exam_options` | Listening/Reading uchun javob variantlari (A, B, C, D) |
| `exam_rubrics` | AI uchun baholash mezonlari (system_prompt, scoring_schema) |
| `exam_attempts` | Foydalanuvchining imtihon urinishi (status, started_at, deadline) |
| `exam_attempt_blocks` | Har bir blokning holati va vaqti |
| `exam_answers` | Foydalanuvchi javoblari (text, audio_url, ai_score) |
| `exam_ai_jobs` | AI (OpenRouter/Whisper) uchun asinxron vazifalar navbati |
| `exam_media` | Yuklangan audio va fayllar reyestri |

*Eslatma: Barcha jadvallar `users.id` ga `ForeignKey` orqali bog'lanadi.*

## 5. API Kontraktlari (Backend API)
Barcha yangi endpointlar `/api/v2/exam/` prefiksi ostida bo'ladi.
* **Auth:** `POST /auth/telegram-login`
* **Exams:** `GET /exams`, `GET /exams/{id}`
* **Attempts:** `POST /exams/{id}/attempts` (Start), `POST /attempts/{id}/submit` (Finish)
* **Answers:** `POST /attempts/{id}/answers` (Save text/options), `POST /.../audio` (Upload voice)
* **Admin:** CRUD operatsiyalari (`/admin/exams`, `/admin/rubrics`, `/admin/attempts`)

## 6. UI Sahifalari (Maestro Exam Web App)
Next.js 14 (App Router) + Tailwind CSS asosida quriladi.
* `/login` — Telegram Login Widget sahifasi.
* `/cabinet` — Shaxsiy kabinet va imtihonlar katalogi.
* `/exam/[attemptId]/instruction` — Imtihon oldi yo'riqnoma va qurilmalarni tekshirish (mic check).
* `/exam/[attemptId]/room` — Asosiy imtihon xonasi (Timer, Navigation, Media Player).
* `/results/[attemptId]` — Batafsil AI tahlili va grafiklar.

## 7. Admin Panel Integratsiyasi
Joriy `admin/` (Next.js) loyihasiga yangi `/exam` routing qo'shiladi.
* **Exam Builder:** Wizard (Qadam-baqadam) orqali imtihon yaratish.
* **Media Manager:** Audio fayllarni yuklash va transkript qilish.
* **AI Rubrics Editor:** Promptlarni va JSON sxemalarni sozlash.
* **Monitoring:** AI job'larning statusini kuzatish (pending, processing, error) va qayta ishga tushirish.

## 8. AI va Texnik Yechimlar
* **Writing:** OpenRouter API orqali baholanadi. AI faqat qat'iy JSON formatida javob qaytarishi shart (Pydantic orqali validatsiya qilinadi).
* **Speaking:** 
  1. Browser `MediaRecorder API` orqali ovoz yozadi.
  2. Serverga yuklanadi.
  3. Speech-to-Text (Whisper API yoki muqobil) orqali transkript qilinadi.
  4. Transkript AI ga yuboriladi.
* **Xavfsizlik:** To'g'ri javoblar (answer_key) client'ga faqat imtihon yakunlanganidan keyin yuboriladi. Timer faqat server tomonidan nazorat qilinadi.

## 9. Rivojlantirish Bosqichlari (Roadmap)

| Bosqich | Vazifa | Holat |
| :--- | :--- | :--- |
| **0** | Backup, eski `exam` kodini va DB jadvallarini tozalash | ⏳ Kutilmoqda |
| **1** | Arxitektura va `MAESTRO_EXAM_PLAN.md` ni tasdiqlash | ✅ Bajarildi |
| **2** | Yangi DB sxemasi (SQLAlchemy models + Alembic migration) | ⏳ Keyingi |
| **3** | Backend API (Auth, Exams, Attempts, Auto-scoring) | ⏳ Kutilmoqda |
| **4** | Admin Panel (Exam CRUD, Media upload, Rubrics) | ⏳ Kutilmoqda |
| **5** | Maestro Exam Web App (Next.js scaffolding, Telegram Auth) | ⏳ Kutilmoqda |
| **6** | Reading & Listening modullari (UI + Auto-check) | ⏳ Kutilmoqda |
| **7** | Writing moduli (AI integration, Text editor) | ⏳ Kutilmoqda |
| **8** | Speaking moduli (Mic recording, STT, AI evaluation) | ⏳ Kutilmoqda |
| **9** | Full Exam (Barchasini birlashtirish, umumiy timer) | ⏳ Kutilmoqda |
| **10**| Telegram Bot integratsiyasi (Mini App, Notifications) | ⏳ Kutilmoqda |

---

### 🚀 Keyingi qadam (Step 2 ga o'tish)

Do'stim, bu `MAESTRO_EXAM_PLAN.md` hujjati sening talablaringga to'liq javob beradimi? 

Agar **HA** bo'lsa, men **Step 2** ga o'taman:
1. **Eski exam modulini tozalash:** Qaysi fayllar va jadvallarni o'chirish kerakligi ro'yxatini tuzaman.
2. **Yangi DB Sxemasi:** 10 ta yangi jadval uchun to'liq SQLAlchemy (async) modellarini va Alembic migratsiya kodini yozib beraman.

Tasdiqlaysanmi yoki planga qandaydir o'zgartirishlar kiritishni xohlaysanmi?
---

# 1. Главная идея Maestro Exam

Мы создаём отдельный продукт:

```text
Maestro Exam
```

Это веб-приложение, куда пользователь заходит через Telegram, видит свой кабинет и может проходить экзамены по английскому языку.

Внутри кабинета будет **5 разделов**:

1. **Full Exam** — полный цикл экзамена.
2. **Listening** — аудирование.
3. **Reading** — чтение.
4. **Writing** — письмо.
5. **Speaking** — говорение.

То есть:

```text
Full Exam = Listening + Reading + Writing + Speaking
```

А также каждый навык можно проходить отдельно.

---

# 2. Как это связано с текущим проектом

Maestro Exam не должен жить отдельно со своей базой данных. Он должен быть частью текущей экосистемы Myestro.

Схема будет такой:

```text
┌────────────────────┐
│   Maestro Exam     │
│   Next.js / React  │
│   Web App          │
└─────────┬──────────┘
          │ HTTP / JWT
          ▼
┌────────────────────┐        ┌────────────────────┐
│   Backend API      │◄──────►│   Admin Panel      │
│   FastAPI          │        │   Next.js          │
└─────────┬──────────┘        └────────────────────┘
          │
          ├──────────────► PostgreSQL
          ├──────────────► Redis
          └──────────────► OpenRouter AI
```

То есть у нас будет:

1. **Текущий Backend API** — общий центр.
2. **Текущая база данных** — общая база.
3. **Текущая админ-панель** — туда добавим новый раздел `Exam`.
4. **Новое веб-приложение** — `Maestro Exam`.
5. Позже подключим **Telegram Mini App / Bot**.

---

# 3. Авторизация пользователя

Ты правильно сказал: авторизация по номеру телефона нам не подходит, потому что основная сущность пользователя завязана на `telegram_id`.

Поэтому используем:

```text
Telegram Login
```

Для веб-приложения будет два сценария.

---

## 3.1. Вход через браузер

Если пользователь открывает Maestro Exam в обычном браузере, используем **Telegram Login Widget**.

Пользователь видит кнопку:

```text
Login with Telegram
```

После нажатия Telegram подтверждает личность и возвращает данные:

```json
{
  "id": 123456789,
  "first_name": "User",
  "last_name": "Name",
  "username": "username",
  "photo_url": "...",
  "auth_date": 1710000000,
  "hash": "..."
}
```

Backend проверяет этот `hash` через токен бота.

Если пользователь существует в базе — логиним его.

Если пользователя ещё нет — создаём базовую запись:

```text
users:
  telegram_id = 123456789
  first_name = ...
  username = ...
  role = user
```

После этого выдаём JWT токен.

Важно:

```text
JWT sub = users.id
```

Не `telegram_id`, а именно `users.id`, как у нас уже устроено в системе.

---

## 3.2. Вход через Telegram внутри бота

Позже, когда мы будем открывать Maestro Exam прямо из Telegram как Mini App, авторизация будет ещё проще.

Telegram Mini App передаёт:

```text
initData
```

Backend проверяет `initData` и понимает, какой это пользователь.

Но это второй этап.

Сначала делаем браузерный вход через Telegram Login.

---

# 4. Что видит пользователь после входа

После входа пользователь попадает в личный кабинет Maestro Exam.

Кабинет состоит из 5 разделов:

```text
1. Full Exam
2. Listening
3. Reading
4. Writing
5. Speaking
```

Также в кабинете должны быть:

```text
- Имя пользователя
- Аватар из Telegram
- Уровень английского, если указан
- История попыток
- Текущая незавершённая попытка
- Результаты
- Прогресс
```

Пример структуры кабинета:

```text
Мой кабинет
├── Полное обследование / Full Exam
├── Listening
├── Reading
├── Writing
├── Speaking
├── Мои результаты
└── Профиль
```

---

# 5. Логика экзаменов

У нас будет два типа экзаменов.

---

## 5.1. Отдельный навык

Например, пользователь выбирает:

```text
Listening
```

И проходит только аудирование.

Или:

```text
Writing
```

И проходит только письмо.

---

## 5.2. Полный цикл

Пользователь выбирает:

```text
Full Exam
```

И проходит сразу:

```text
Listening → Reading → Writing → Speaking
```

Порядок модулей можно настроить в админке.

Например:

```text
1. Listening
2. Reading
3. Writing
4. Speaking
```

Или другой порядок.

---

# 6. Сущности новой базы данных

Старые таблицы `exam*` мы удаляем и строим новую схему с нуля.

Но сначала обязательно делаем резервную копию базы данных.

---

## 6.1. Основные таблицы

Предлагаю следующую структуру.

---

### 1. `exams`

Это сам экзамен.

```text
exams
├── id
├── code
├── title
├── description
├── exam_type
├── cefr_level
├── time_limit_sec
├── is_published
├── scoring_config
├── created_at
└── updated_at
```

`exam_type`:

```text
full
listening
reading
writing
speaking
```

Примеры:

```text
code = full_exam_b1
title = Full Exam B1
exam_type = full

code = listening_a2
title = Listening Practice A2
exam_type = listening
```

---

### 2. `exam_blocks`

Это блоки внутри экзамена.

Для отдельного экзамена, например `Listening`, это может быть один или несколько блоков.

Для `Full Exam` это будут четыре блока:

```text
listening
reading
writing
speaking
```

Поля:

```text
exam_blocks
├── id
├── exam_id
├── block_type
├── title
├── description
├── instructions
├── order
├── time_limit_sec
├── config
├── created_at
└── updated_at
```

`block_type`:

```text
listening
reading
writing
speaking
```

---

### 3. `exam_items`

Это конкретные задания внутри блока.

Например:

```text
- один вопрос аудирования
- один текст чтения
- одно задание на письмо
- одна тема для говорения
```

Поля:

```text
exam_items
├── id
├── block_id
├── item_type
├── title
├── instruction
├── question_text
├── passage_text
├── audio_url
├── audio_duration_sec
├── transcript_text
├── min_words
├── max_words
├── preparation_time_sec
├── answer_time_sec
├── max_score
├── order
├── config
├── answer_key
├── rubric_id
└── created_at
```

`item_type`:

```text
listening_question
reading_question
writing_task
speaking_task
```

---

### 4. `exam_options`

Это варианты ответов для тестовых вопросов.

Используется для Listening и Reading.

```text
exam_options
├── id
├── item_id
├── text
├── is_correct
├── order
└── created_at
```

---

### 5. `exam_rubrics`

Это шаблоны оценки для AI.

Особенно важно для:

```text
Writing
Speaking
```

Поля:

```text
exam_rubrics
├── id
├── code
├── name
├── skill_type
├── system_prompt
├── user_prompt_template
├── scoring_schema
├── cefr_mapping
├── is_active
└── created_at
```

Пример:

```text
code = writing_b1_v1
name = Writing B1 Evaluation
skill_type = writing
```

---

### 6. `exam_attempts`

Это попытка пользователя пройти экзамен.

```text
exam_attempts
├── id
├── user_id
├── exam_id
├── status
├── started_at
├── submitted_at
├── completed_at
├── total_score
├── cefr_estimate
├── metadata
└── created_at
```

`status`:

```text
created
in_progress
submitted
scoring
completed
needs_review
failed
```

---

### 7. `exam_attempt_blocks`

Это состояние каждого блока внутри попытки.

```text
exam_attempt_blocks
├── id
├── attempt_id
├── block_id
├── status
├── started_at
├── completed_at
├── score
└── metadata
```

---

### 8. `exam_answers`

Это ответы пользователя.

```text
exam_answers
├── id
├── attempt_id
├── item_id
├── selected_options
├── text_answer
├── audio_url
├── transcript_text
├── auto_score
├── ai_score
├── final_score
├── ai_status
├── feedback
└── created_at
```

`ai_status`:

```text
pending
processing
completed
error
needs_review
```

---

### 9. `exam_ai_jobs`

Это очередь задач для AI.

Например:

```text
- проверить writing
- расшифровать speaking
- оценить speaking
```

Поля:

```text
exam_ai_jobs
├── id
├── attempt_id
├── answer_id
├── job_type
├── status
├── provider
├── request_payload
├── response_payload
├── error_message
├── attempts_count
├── created_at
└── updated_at
```

---

### 10. `exam_media`

Это файлы: аудио, изображения, документы.

```text
exam_media
├── id
├── owner_type
├── owner_id
├── file_type
├── file_name
├── file_path
├── mime_type
├── size_bytes
├── duration_sec
├── transcript_text
└── created_at
```

---

# 7. Какие типы заданий будут поддерживаться

---

## 7.1. Listening

Для аудирования.

Формат:

```text
1. Пользователь слушает аудио.
2. Отвечает на вопрос.
3. Ответ проверяется автоматически.
```

Типы вопросов:

```text
- один правильный ответ
- несколько правильных ответов
- сопоставление
- ввод короткого ответа
```

Для MVP начнём с:

```text
- один правильный ответ
- несколько правильных ответов
- короткий ответ
```

---

## 7.2. Reading

Для чтения.

Формат:

```text
1. Пользователь читает текст.
2. Отвечает на вопросы.
3. Ответы проверяются автоматически.
```

Типы вопросов:

```text
- выбор одного ответа
- выбор нескольких ответов
- правда/ложь
- короткий ответ
```

---

## 7.3. Writing

Для письма.

Формат:

```text
1. Пользователь получает задание.
2. Пишет текст.
3. Отправляет.
4. AI проверяет текст.
5. Пользователь получает оценку и обратную связь.
```

Пример задания:

```text
Write an email to your friend about your last holiday.
Write 80-120 words.
```

AI оценивает:

```text
- Task Achievement
- Coherence and Cohesion
- Lexical Resource
- Grammar
- Spelling
```

---

## 7.4. Speaking

Для говорения.

Формат:

```text
1. Пользователь получает тему.
2. Есть время на подготовку.
3. Пользователь записывает голос.
4. Аудио отправляется на сервер.
5. Система делает транскрипцию.
6. AI оценивает ответ.
7. Пользователь получает результат.
```

Пример:

```text
Describe your favourite teacher.
You have 30 seconds to prepare.
Speak for 60 seconds.
```

AI оценивает:

```text
- Fluency
- Vocabulary
- Grammar
- Relevance to topic
- Length and completeness
```

Важно:

```text
Оценка произношения без отдельного специализированного сервиса будет ограниченной.
Поэтому сначала можно оценивать речь через транскрипт.
Позже можно добавить отдельный pronunciation scoring.
```

---

# 8. Как должен проходить Full Exam

Пользователь выбирает:

```text
Full Exam
```

Система создаёт одну попытку:

```text
exam_attempts
```

Внутри этой попытки создаются четыре блока:

```text
listening_block
reading_block
writing_block
speaking_block
```

Пример:

```text
Full Exam Attempt
├── Listening
├── Reading
├── Writing
└── Speaking
```

Пользователь проходит их по очереди.

Экраны:

```text
1. Инструкции к полному экзамену
2. Проверка устройства
3. Listening
4. Reading
5. Writing
6. Speaking
7. Завершение
```

Перед Speaking нужно проверить микрофон:

```text
- микрофон доступен
- запись работает
- пользователь слышит себя
```

---

# 9. Пользовательский путь

---

## 9.1. Вход

```text
1. Пользователь открывает Maestro Exam.
2. Нажимает Login with Telegram.
3. Backend проверяет пользователя.
4. Пользователь попадает в кабинет.
```

---

## 9.2. Выбор экзамена

```text
1. Пользователь выбирает раздел.
2. Видит доступные экзамены.
3. Видит описание, уровень, время, количество вопросов.
4. Нажимает Start.
```

---

## 9.3. Инструкция

Перед стартом показываем:

```text
- название экзамена
- время
- количество заданий
- правила
- рекомендации
- требования к устройству
```

Для Speaking отдельно:

```text
- нужен микрофон
- тихое место
- наушники рекомендуются
```

---

## 9.4. Прохождение

```text
1. Пользователь выполняет задания.
2. Ответы автоматически сохраняются.
3. Таймер контролируется сервером.
4. Нельзя получить правильные ответы до завершения.
```

---

## 9.5. Завершение

```text
1. Пользователь завершает экзамен.
2. Объективные вопросы проверяются сразу.
3. Writing и Speaking отправляются в AI.
4. Пользователь видит статус "Оценивается".
5. После оценки видит результат.
```

---

# 10. Результаты

Для каждой попытки показываем:

```text
- общий балл
- балл по каждому навыку
- предполагаемый уровень CEFR
- обратная связь от AI
- ошибки
- рекомендации
- историю попыток
```

Пример:

```text
Full Exam Result
├── Overall: 72/100
├── Listening: 80/100
├── Reading: 75/100
├── Writing: 68/100
├── Speaking: 65/100
└── Estimated level: B1+
```

Для Writing:

```text
- Task achievement
- Coherence
- Vocabulary
- Grammar
- Corrected sentences
- Recommendations
```

Для Speaking:

```text
- Transcript
- Fluency
- Grammar
- Vocabulary
- Weak places
- Recommendations
```

---

# 11. Как работает AI-оценка

AI нужен для двух модулей:

```text
Writing
Speaking
```

Для Listening и Reading ответы можно проверять автоматически.

---

## 11.1. Writing

Пользователь отправляет текст.

Backend формирует запрос к AI.

В запрос передаём:

```text
- задание
- требуемый уровень
- ответ пользователя
- критерии оценки
- максимальный балл
- формат ответа
```

AI должен вернуть строго JSON.

Пример:

```json
{
  "overall_score": 74,
  "cefr_estimate": "B1",
  "criteria": [
    {
      "name": "Task Achievement",
      "score": 8,
      "max_score": 10,
      "comment": "The task is mostly completed."
    },
    {
      "name": "Coherence",
      "score": 7,
      "max_score": 10,
      "comment": "Some linking words are missing."
    },
    {
      "name": "Lexical Resource",
      "score": 7,
      "max_score": 10,
      "comment": "Vocabulary is acceptable but repetitive."
    },
    {
      "name": "Grammar",
      "score": 6,
      "max_score": 10,
      "comment": "There are frequent tense mistakes."
    }
  ],
  "corrections": [
    {
      "original": "I go to Samarkand last year.",
      "corrected": "I went to Samarkand last year.",
      "explanation": "Use Past Simple for completed past actions."
    }
  ],
  "strengths": [
    "Good structure",
    "Clear answer"
  ],
  "weaknesses": [
    "Past tense errors",
    "Limited vocabulary"
  ],
  "recommendations": [
    "Practice Past Simple",
    "Use more linking words"
  ]
}
```

---

## 11.2. Speaking

Для Speaking процесс сложнее.

Шаги:

```text
1. Пользователь записывает аудио.
2. Аудио сохраняется.
3. Создаётся задача на транскрипцию.
4. Транскрипт сохраняется.
5. Транскрипт отправляется в AI.
6. AI возвращает оценку.
```

Пример:

```text
Audio → Speech-to-Text → AI Evaluation → Result
```

AI получает:

```text
- тему задания
- требуемый уровень
- транскрипт ответа
- длительность ответа
- критерии оценки
```

AI возвращает JSON, похожий на Writing.

Дополнительно можно считать простые метрики:

```text
- количество слов
- темп речи
- количество пауз
- длительность ответа
```

Но для точной оценки пауз и произношения нужен отдельный аудио-анализ.

---

# 12. Шаблоны оценки

В админке должны быть шаблоны для AI.

Например:

```text
Writing A1 Rubric
Writing A2 Rubric
Writing B1 Rubric
Speaking A2 Rubric
Speaking B1 Rubric
Full Exam CEFR Mapping
```

Каждый шаблон содержит:

```text
- системный промпт
- пользовательский промпт
- критерии
- веса критериев
- максимальный балл
- JSON-формат ответа
```

Это позволит легко менять логику оценки без изменения кода.

---

# 13. Как будет устроен новый раздел в админ-панели

В текущую админ-панель добавляем новый блок:

```text
Exam
```

Он должен быть отдельным модулем.

Не смешиваем его со старым `tests`, если `tests` является отдельной сущностью.

---

## 13.1. Структура админ-раздела

```text
Exam
├── Dashboard
├── Exams
├── Blocks
├── Questions / Tasks
├── Rubrics
├── Attempts
├── AI Jobs
└── Settings
```

---

## 13.2. Dashboard

Показывает:

```text
- количество экзаменов
- количество попыток
- средние баллы
- количество завершённых попыток
- ошибки AI
- попытки на ручной проверке
```

---

## 13.3. Exams

Здесь админ создаёт экзамены.

Поля:

```text
- название
- код
- тип
- уровень
- описание
- общее время
- опубликован или нет
- порядок модулей
- веса навыков
```

Типы:

```text
full
listening
reading
writing
speaking
```

---

## 13.4. Blocks

Внутри экзамена админ управляет блоками.

Например, для `Full Exam`:

```text
Listening block
Reading block
Writing block
Speaking block
```

Для каждого блока:

```text
- название
- инструкция
- время
- порядок
- активен или нет
```

---

## 13.5. Questions / Tasks

Здесь админ добавляет задания.

Для Listening:

```text
- загрузить аудио
- добавить вопрос
- добавить варианты ответа
- отметить правильный ответ
- указать балл
```

Для Reading:

```text
- добавить текст
- добавить вопрос
- добавить варианты ответа
- отметить правильный ответ
- указать балл
```

Для Writing:

```text
- добавить задание
- минимальное количество слов
- максимальное количество слов
- выбрать рубрику
- максимальный балл
```

Для Speaking:

```text
- добавить тему
- время подготовки
- время ответа
- выбрать рубрику
- максимальный балл
```

---

## 13.6. Rubrics

Здесь админ управляет AI-шаблонами.

Поля:

```text
- название
- навык
- системный промпт
- шаблон запроса
- критерии
- веса
- JSON schema
- активен или нет
```

---

## 13.7. Attempts

Здесь админ видит попытки пользователей.

Можно смотреть:

```text
- пользователь
- экзамен
- статус
- дата
- общий балл
- баллы по блокам
- ответы
- AI feedback
- аудио
- транскрипт
```

Также админ может:

```text
- изменить финальный балл вручную
- отправить на повторную AI-оценку
- отметить как needs_review
- завершить попытку принудительно
```

---

## 13.8. AI Jobs

Здесь видны задачи обработки:

```text
- pending
- processing
- completed
- error
```

Если AI упал, админ может перезапустить задачу.

---

# 14. Удобство добавления экзамена в админке

Нужно сделать так, чтобы админ мог легко добавить экзамен без программиста.

Рекомендую сделать мастер создания:

```text
Step 1. Выбрать тип экзамена
Step 2. Заполнить основную информацию
Step 3. Настроить блоки
Step 4. Добавить задания
Step 5. Настроить оценку
Step 6. Предпросмотр
Step 7. Публикация
```

---

## 14.1. Пример создания Listening

```text
1. Админ выбирает тип: Listening
2. Пишет название: Listening A2 Practice
3. Указывает уровень: A2
4. Указывает время: 20 минут
5. Добавляет блок: Part 1
6. Загружает аудио
7. Добавляет вопрос
8. Добавляет варианты ответа
9. Отмечает правильный ответ
10. Сохраняет
11. Публикует
```

---

## 14.2. Пример создания Writing

```text
1. Админ выбирает тип: Writing
2. Пишет название: Writing B1 Email Task
3. Добавляет задание
4. Указывает минимум слов: 80
5. Указывает максимум слов: 120
6. Выбирает AI-рубрику
7. Указывает максимальный балл
8. Публикует
```

---

## 14.3. Пример создания Speaking

```text
1. Админ выбирает тип: Speaking
2. Пишет название: Speaking B1 Topic
3. Добавляет тему
4. Указывает время подготовки: 30 секунд
5. Указывает время ответа: 60 секунд
6. Выбирает AI-рубрику
7. Публикует
```

---

# 15. UX/UI для каждого модуля

---

## 15.1. Listening UX

Экран аудирования:

```text
┌────────────────────────────────────┐
│ Listening Task 1                   │
│                                    │
│ Audio player                       │
│ ▶ 00:00 / 01:20                    │
│                                    │
│ Question:                          │
│ Where does the conversation take   │
│ place?                             │
│                                    │
│ ○ At school                        │
│ ○ At home                          │
│ ○ At a shop                        │
│ ○ At a hospital                    │
│                                    │
│ [Previous]        [Next]           │
└────────────────────────────────────┘
```

Правила:

```text
- аудио можно ограничить количеством прослушиваний
- можно разрешить 1 или 2 прослушивания
- нельзя показывать правильные ответы до завершения
- ответ сохраняется автоматически
- таймер должен быть серверным
```

---

## 15.2. Reading UX

Экран чтения:

```text
┌────────────────────────────────────┐
│ Reading Task 1                     │
│                                    │
│ Passage                            │
│ Lorem ipsum dolor sit amet...      │
│                                    │
│ Question 1                         │
│ What is the main idea?             │
│                                    │
│ ○ Option A                         │
│ ○ Option B                         │
│ ○ Option C                         │
│ ○ Option D                         │
│                                    │
│ [Previous]        [Next]           │
└────────────────────────────────────┘
```

Можно сделать две колонки:

```text
Слева текст
Справа вопросы
```

---

## 15.3. Writing UX

Экран письма:

```text
┌────────────────────────────────────┐
│ Writing Task                       │
│                                    │
│ Write an email to your friend...   │
│                                    │
│ 80-120 words                       │
│                                    │
│ ┌────────────────────────────────┐ │
│ │                                │ │
│ │                                │ │
│ │                                │ │
│ └────────────────────────────────┘ │
│                                    │
│ Words: 0 / 120                     │
│                                    │
│ [Save Draft]      [Submit]         │
└────────────────────────────────────┘
```

Функции:

```text
- счётчик слов
- автосохранение
- черновик
- подтверждение перед отправкой
- проверка минимального количества слов
```

---

## 15.4. Speaking UX

Экран говорения:

```text
┌────────────────────────────────────┐
│ Speaking Task                      │
│                                    │
│ Describe your favourite teacher.   │
│                                    │
│ Preparation: 30 seconds            │
│ Answer time: 60 seconds            │
│                                    │
│ [Start Preparation]                │
│                                    │
└────────────────────────────────────┘
```

После подготовки:

```text
┌────────────────────────────────────┐
│ Ready to record                    │
│                                    │
│ [Start Recording]                  │
│                                    │
└────────────────────────────────────┘
```

Во время записи:

```text
┌────────────────────────────────────┐
│ Recording...                       │
│ 00:12 / 01:00                      │
│                                    │
│ [Stop]                             │
└────────────────────────────────────┘
```

После записи:

```text
┌────────────────────────────────────┐
│ Your answer                        │
│                                    │
│ ▶ Play recording                   │
│                                    │
│ [Record Again]    [Submit Answer]  │
└────────────────────────────────────┘
```

Технически используем:

```text
MediaRecorder API
```

Форматы:

```text
audio/webm
audio/mp4 fallback
```

Нужно обязательно проверять:

```text
- доступ к микрофону
- поддержку записи браузером
- размер файла
- длительность записи
```

---

# 16. Таймеры и безопасность

Таймер должен контролироваться сервером.

Нельзя доверять только клиенту.

Когда пользователь начинает попытку:

```text
Backend сохраняет:
  started_at
  time_limit_sec
  deadline
```

Когда пользователь отправляет ответ:

```text
Backend проверяет:
  не истекло ли время
```

Если время вышло:

```text
- автоматически завершаем блок
- отправляем сохранённые ответы
- если ответов нет, помечаем как пустые
```

Также нужно защитить данные:

```text
- правильные ответы не отправлять на клиент до завершения
- медиафайлы отдавать только авторизованному пользователю
- чужие попытки нельзя смотреть
- админ имеет доступ через отдельную роль
```

---

# 17. Синхронизация с текущей админ-панелью

В текущей админке мы добавляем новый раздел:

```text
/admin/exam
```

Или просто:

```text
/exam
```

Он будет работать через текущий Backend API.

Админка будет управлять:

```text
- экзаменами
- блоками
- вопросами
- медиа
- рубриками
- попытками
- AI-задачами
```

То есть админ управляет контентом, а Maestro Exam отображает этот контент пользователю.

---

# 18. Синхронизация с Telegram

Это будет позже, но архитектурно нужно заложить сразу.

Позже мы сможем:

```text
1. Открывать Maestro Exam из бота.
2. Показывать результаты в боте.
3. Отправлять уведомления:
   - экзамен завершён
   - результат готов
   - AI завершил проверку
4. Давать ссылку на подробный разбор.
```

Например, бот будет говорить:

```text
Your Writing result is ready.
Score: 72/100
Open Maestro Exam to see details.
```

---

# 19. Новая структура проекта

Предлагаю добавить отдельную папку:

```text
MyestroEco/
├── admin/
├── telegram_bot/
└── exam/
```

Где:

```text
exam/ = Maestro Exam web app
```

Внутри:

```text
exam/
├── Dockerfile
├── next.config.js
├── package.json
├── tailwind.config.ts
├── tsconfig.json
└── app/
    ├── login/
    ├── cabinet/
    ├── exams/
    ├── attempt/
    ├── results/
    └── profile/
```

Компоненты:

```text
exam/components/
├── auth/
├── layout/
├── dashboard/
├── exam/
│   ├── listening/
│   ├── reading/
│   ├── writing/
│   ├── speaking/
│   └── shared/
├── ui/
└── results/
```

---

# 20. Новая структура бэкенда для экзамена

Чтобы не смешивать старый и новый код, можно временно использовать версию:

```text
/api/v2/exam
```

Или после удаления старого:

```text
/api/exam
```

Я бы рекомендовал новый модуль:

```text
telegram_bot/backend/app/api/exam_v2/
```

Структура:

```text
api/exam_v2/
├── router.py
├── auth.py
├── exams.py
├── attempts.py
├── answers.py
├── media.py
├── results.py
└── admin.py
```

Модели:

```text
models/exam_v2/
├── exam.py
├── block.py
├── item.py
├── option.py
├── rubric.py
├── attempt.py
├── answer.py
├── ai_job.py
└── media.py
```

Сервисы:

```text
services/exam/
├── scoring_service.py
├── ai_evaluation_service.py
├── transcription_service.py
├── media_service.py
├── attempt_service.py
└── telegram_auth_service.py
```

---

# 21. API для Maestro Exam

Ниже примерный контракт.

---

## 21.1. Авторизация

```text
POST /api/v2/exam/auth/telegram/login
```

Входные данные:

```json
{
  "id": 123456789,
  "first_name": "User",
  "last_name": "Name",
  "username": "username",
  "photo_url": "...",
  "auth_date": 1710000000,
  "hash": "..."
}
```

Ответ:

```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "telegram_id": 123456789,
    "first_name": "User",
    "username": "username",
    "cefr_level": "B1"
  }
}
```

---

## 21.2. Получить профиль

```text
GET /api/v2/exam/me
```

---

## 21.3. Получить доступные экзамены

```text
GET /api/v2/exam/exams?type=listening
```

Типы:

```text
full
listening
reading
writing
speaking
```

Ответ:

```json
{
  "items": [
    {
      "id": 1,
      "code": "listening_a2",
      "title": "Listening A2",
      "exam_type": "listening",
      "cefr_level": "A2",
      "time_limit_sec": 1200,
      "description": "..."
    }
  ]
}
```

---

## 21.4. Начать попытку

```text
POST /api/v2/exam/exams/{exam_id}/attempts
```

Ответ:

```json
{
  "attempt_id": 100,
  "status": "in_progress",
  "blocks": [
    {
      "id": 1,
      "block_type": "listening",
      "title": "Listening Part",
      "time_limit_sec": 1200,
      "status": "pending"
    }
  ]
}
```

---

## 21.5. Получить текущее состояние попытки

```text
GET /api/v2/exam/attempts/{attempt_id}
```

---

## 21.6. Получить задания блока

```text
GET /api/v2/exam/attempts/{attempt_id}/blocks/{block_id}
```

Важно:

```text
Не возвращаем правильные ответы.
```

---

## 21.7. Сохранить ответ

```text
POST /api/v2/exam/attempts/{attempt_id}/answers
```

Для выбора:

```json
{
  "item_id": 15,
  "selected_options": [3]
}
```

Для writing:

```json
{
  "item_id": 20,
  "text_answer": "I went to Samarkand..."
}
```

---

## 21.8. Загрузить аудио для Speaking

```text
POST /api/v2/exam/attempts/{attempt_id}/answers/{answer_id}/audio
```

Формат:

```text
multipart/form-data
```

---

## 21.9. Завершить блок

```text
POST /api/v2/exam/attempts/{attempt_id}/blocks/{block_id}/complete
```

---

## 21.10. Завершить экзамен

```text
POST /api/v2/exam/attempts/{attempt_id}/submit
```

---

## 21.11. Получить результат

```text
GET /api/v2/exam/attempts/{attempt_id}/result
```

---

## 21.12. Получить статус AI-оценки

```text
GET /api/v2/exam/attempts/{attempt_id}/ai-status
```

Или можно использовать polling сначала.

Позже можно сделать WebSocket или SSE.

---

# 22. Админ API

Отдельные эндпоинты для админки:

```text
POST   /api/v2/exam/admin/exams
GET    /api/v2/exam/admin/exams
GET    /api/v2/exam/admin/exams/{id}
PUT    /api/v2/exam/admin/exams/{id}
DELETE /api/v2/exam/admin/exams/{id}

POST   /api/v2/exam/admin/exams/{id}/blocks
PUT    /api/v2/exam/admin/blocks/{id}
DELETE /api/v2/exam/admin/blocks/{id}

POST   /api/v2/exam/admin/blocks/{id}/items
PUT    /api/v2/exam/admin/items/{id}
DELETE /api/v2/exam/admin/items/{id}

POST   /api/v2/exam/admin/items/{id}/options
PUT    /api/v2/exam/admin/options/{id}
DELETE /api/v2/exam/admin/options/{id}

POST   /api/v2/exam/admin/rubrics
PUT    /api/v2/exam/admin/rubrics/{id}

GET    /api/v2/exam/admin/attempts
GET    /api/v2/exam/admin/attempts/{id}
POST   /api/v2/exam/admin/attempts/{id}/revalidate
```

---

# 23. Удаление старого exam-модуля

Перед удалением делаем:

```text
1. pg_dump базы данных
2. отдельный дамп таблиц exam*
3. фиксацию текущего коммита
```

Затем удаляем:

```text
- старые таблицы:
  exams
  exam_sections
  exam_questions
  exam_attempts
  exam_answers
```

```text
- старые файлы бэкенда, связанные с exam
- старые роутеры /api/exams
- старые bot handlers exam
- старые админские компоненты exam, если они относятся именно к экзаменам
```

Но важно:

```text
Не трогаем модуль tests, если он является отдельной функцией и не связан с exam.
```

После удаления создаём новую миграцию:

```text
drop old exam tables
create new exam tables
```

---

# 24. Docker

Добавим новый сервис:

```text
maestro-exam
```

Пример:

```yaml
exam:
  build:
    context: ./exam
  container_name: maestro-exam
  ports:
    - "3003:3000"
  environment:
    - NEXT_PUBLIC_API_URL=http://backend:8000
  depends_on:
    - backend
  networks:
    - myestro-net
```

Так как у нас уже есть сеть:

```text
myestro-net
```

новый сервис будет видеть:

```text
backend
postgres
redis
```

---

# 25. Этапы реализации

---

## Этап 0. Подготовка

Цель:

```text
Зафиксировать текущее состояние и безопасно удалить старый exam.
```

Задачи:

```text
1. Сделать backup PostgreSQL.
2. Отдельно сохранить old exam tables.
3. Найти все места, где используется старый exam.
4. Отключить старый exam из бота.
5. Удалить старые таблицы.
6. Удалить старый код.
7. Подготовить чистую ветку для нового модуля.
```

---

## Этап 1. Архитектура и документы

Цель:

```text
Утвердить схему данных, API, UX и админ-панель.
```

Создаём:

```text
MAESTRO_EXAM_PLAN.md
```

Содержимое:

```text
- цель
- роли
- сценарии пользователя
- схема БД
- API
- UI страницы
- админ-панель
- AI evaluation
- этапы разработки
```

---

## Этап 2. Новая база данных

Цель:

```text
Создать новую схему для экзаменов.
```

Делаем:

```text
- новые модели SQLAlchemy
- Alembic migration
- индексы
- связи с users
- JSONB поля для гибкости
```

---

## Этап 3. Backend API для экзаменов

Цель:

```text
Сделать базовый API для веб-приложения.
```

Сначала:

```text
- список экзаменов
- старт попытки
- получение блоков
- сохранение ответа
- завершение попытки
- автоматическая проверка Listening/Reading
```

---

## Этап 4. Админ-панель для управления экзаменами

Цель:

```text
Чтобы админ мог создавать экзамены без кода.
```

Делаем:

```text
- список экзаменов
- создание экзамена
- создание блоков
- создание заданий
- загрузка аудио
- добавление вариантов ответа
- управление рубриками
- публикация
```

---

## Этап 5. Каркас Maestro Exam

Цель:

```text
Поднять отдельное веб-приложение.
```

Делаем:

```text
- Next.js app
- авторизация через Telegram
- кабинет пользователя
- 5 разделов
- список доступных экзаменов
- история попыток
```

---

## Этап 6. Модуль Reading

Цель:

```text
Самый простой модуль для запуска.
```

Делаем:

```text
- отображение текста
- вопросы
- варианты ответа
- автосохранение
- автопроверка
- результат
```

Почему начинаем с Reading:

```text
Он проще всего технически.
Нет аудио.
Нет записи.
Нет сложного AI.
```

---

## Этап 7. Модуль Listening

Цель:

```text
Добавить аудио и автопроверку.
```

Делаем:

```text
- аудио плеер
- ограничение прослушиваний
- вопросы
- автопроверка
- результат
```

---

## Этап 8. Модуль Writing

Цель:

```text
Подключить AI-оценку текста.
```

Делаем:

```text
- текстовый редактор
- счётчик слов
- автосохранение
- отправка в AI
- JSON-ответ от AI
- отображение результата
```

---

## Этап 9. Модуль Speaking

Цель:

```text
Добавить запись голоса и AI-оценку речи.
```

Делаем:

```text
- доступ к микрофону
- запись аудио
- загрузка на сервер
- транскрипция
- AI-оценка
- результат
```

Это самый сложный модуль, поэтому делаем его после Writing.

---

## Этап 10. Full Exam

Цель:

```text
Объединить четыре модуля в один полный экзамен.
```

Делаем:

```text
- один attempt
- четыре блока
- последовательный переход
- общий таймер или таймеры блоков
- общий результат
- оценка по каждому навыку
```

---

## Этап 11. Результаты и аналитика

Цель:

```text
Сделать понятные результаты для пользователя и админа.
```

Делаем:

```text
- страницу результата
- графики
- CEFR estimate
- feedback от AI
- историю попыток
- админ-аналитику
```

---

## Этап 12. Интеграция с Telegram

Цель:

```text
Связать Maestro Exam с ботом.
```

Делаем:

```text
- кнопка в боте
- открытие как Mini App
- уведомления о результатах
- синхронизация профиля
- передача прогресса
```

---

# 26. Что нужно для Speaking

Для Speaking нужно решить три технических вопроса.

---

## 26.1. Запись аудио

Используем браузер:

```text
MediaRecorder API
```

Нужно поддерживать:

```text
Chrome
Edge
Firefox
Safari
Mobile browsers
```

---

## 26.2. Хранение аудио

Варианты:

```text
1. Локальный volume внутри Docker
2. S3-compatible storage
3. Railway volume
```

Для MVP можно:

```text
локальное хранилище
```

Для продакшена лучше:

```text
S3-compatible storage
```

---

## 26.3. Транскрипция

Нужен Speech-to-Text сервис.

Варианты:

```text
1. OpenAI Whisper API
2. Google Speech-to-Text
3. Azure Speech
4. Deepgram
5. Local Whisper
```

Для MVP лучше всего:

```text
Whisper API или аналог
```

Если пока нет ключа для Speech-to-Text, можно временно:

```text
- сохранять аудио
- помечать как needs_review
- оценивать вручную
```

Но полноценный Speaking без транскрипции будет работать слабо.

---

# 27. Оценка и баллы

Предлагаю единую систему:

```text
0-100 баллов
```

Каждый навык имеет вес.

Для Full Exam:

```text
Listening = 25%
Reading = 25%
Writing = 25%
Speaking = 25%
```

Но веса можно настроить в админке.

Пример:

```json
{
  "listening_weight": 25,
  "reading_weight": 25,
  "writing_weight": 25,
  "speaking_weight": 25
}
```

Итоговый балл:

```text
total = listening_score * 0.25
      + reading_score * 0.25
      + writing_score * 0.25
      + speaking_score * 0.25
```

CEFR estimate можно задавать таблицей:

```text
0-39  A1
40-54 A2
55-69 B1
70-84 B2
85-100 C1
```

Это тоже должно быть настраиваемым.

---

# 28. Риски и как их закрыть

---

## Риск 1. AI вернёт невалидный JSON

Решение:

```text
- просить только JSON
- использовать Pydantic validation
- делать 3 попытки
- если не получилось, помечать как needs_review
```

---

## Риск 2. Аудио не записывается в Safari

Решение:

```text
- проверить поддержку форматов
- использовать fallback
- разрешить загрузку файла вручную
```

---

## Риск 3. Транскрипция плохого качества

Решение:

```text
- показывать пользователю рекомендации
- использовать хороший STT сервис
- разрешать ручную проверку админом
```

---

## Риск 4. Долгая AI-обработка

Решение:

```text
- асинхронные задачи
- статус "Оценивается"
- уведомление после готовности
```

---

## Риск 5. Пользователь обновил страницу во время экзамена

Решение:

```text
- серверная попытка
- автосохранение ответов
- восстановление текущего состояния
```

---

## Риск 6. Списывание

Полностью защитить сложно, но можно добавить:

```text
- предупреждение при переключении вкладки
- логирование времени
- ограничение времени
- запрет копирования текста
- один активный поток
```

Для строгого экзамена нужен proctoring, но это уже отдельный большой продукт.

---

# 29. Что не должно войти в первый MVP

Чтобы не перегрузить систему, сначала не делаем:

```text
- оплату
- сертификаты в PDF
- сложный proctoring
- произношение с фонетической оценкой
- видео-интервью
- живой экзаменатор
- мобильное приложение
- сложную аналитику по каждому слову
- мультиязычный AI feedback, кроме нужного нам языка
```

MVP должен быть:

```text
чистый, стабильный и рабочий
```

---

# 30. Итоговая формулировка продукта

Maestro Exam — это веб-платформа внутри экосистемы Myestro, где пользователь может:

```text
- войти через Telegram
- выбрать полный экзамен или отдельный навык
- пройти Listening, Reading, Writing и Speaking
- получить автоматическую проверку для тестовых частей
- получить AI-оценку для Writing и Speaking
- увидеть подробный результат и рекомендации
```

Администратор при этом может:

```text
- создавать экзамены
- добавлять блоки
- добавлять задания
- загружать аудио
- управлять рубриками
- смотреть попытки
- контролировать AI-оценку
```

Всё это работает:

```text
- на общем Backend API
- на общей базе данных
- с общей системой пользователей
- с общей авторизацией через Telegram
- с общей админ-панелью
```

---

# 31. Что нужно решить перед стартом кода

Перед тем как писать код, нам нужно подтвердить несколько решений.

---

## Решение 1. Создание пользователя

Если пользователь впервые заходит в Maestro Exam через Telegram Login, что делать?

Варианты:

```text
A. Создавать пользователя автоматически.
B. Требовать сначала зарегистрироваться в боте.
```

Я рекомендую для MVP:

```text
A. Создавать автоматически базовую запись.
```

А потом внутри веб-приложения попросить заполнить профиль.

---

## Решение 2. Хранение аудио

Варианты:

```text
A. Локальный volume.
B. S3 storage.
```

Для MVP:

```text
A. Локальный volume.
```

Для продакшена:

```text
B. S3.
```

---

## Решение 3. Транскрипция

Нужен ли сразу Speech-to-Text сервис?

Я рекомендую:

```text
Да, для Speaking он нужен обязательно.
```

Иначе Speaking будет только ручной проверкой.

---

## Решение 4. Порядок модулей в Full Exam

Рекомендую:

```text
Listening → Reading → Writing → Speaking
```

Но можно сделать настраиваемым.

---

## Решение 5. Можно ли прервать экзамен?

Варианты:

```text
A. Можно продолжить позже.
B. Нельзя, попытка должна быть завершена за один раз.
```

Для MVP лучше:

```text
A. Можно продолжить позже, но с серверным дедлайном.
```

Или более строго:

```text
B. Только одна сессия, после выхода попытка завершается.
```

Я бы выбрал гибкий вариант для обучения, но строгий для реального экзамена.

---

# 32. Мой рекомендуемый порядок работы

Я предлагаю действовать так:

```text
Шаг 1. Утвердить эту концепцию.
Шаг 2. Подготовить MAESTRO_EXAM_PLAN.md.
Шаг 3. Спроектировать новую схему БД.
Шаг 4. Удалить старый exam.
Шаг 5. Создать новые таблицы.
Шаг 6. Сделать Backend API.
Шаг 7. Сделать админ-панель для управления экзаменами.
Шаг 8. Сделать Maestro Exam веб-приложение.
Шаг 9. Подключить AI для Writing.
Шаг 10. Подключить запись и AI для Speaking.
Шаг 11. Собрать Full Exam.
Шаг 12. Подключить Telegram Mini App.
```

---

# 33. Короткий ответ по сути

Мы делаем:

```text
Отдельное веб-приложение Maestro Exam
```

Оно:

```text
- внутри проекта Myestro
- использует тот же Backend
- использует ту же базу данных
- использует тех же пользователей
- авторизуется через Telegram
- имеет 5 разделов
- проверяет тесты автоматически
- проверяет Writing и Speaking через AI
- управляется через текущую админ-панель
```

Старый экзамен:

```text
удаляем после резервной копии
```

Новый экзамен:

```text
строим с нуля, чисто, модульно и масштабируемо
```

---

Если эта концепция тебе подходит, дальше я могу сразу сделать следующий шаг:

```text
1. Подготовить финальный MAESTRO_EXAM_PLAN.md
2. Расписать новую схему базы данных
3. Подготовить список файлов, которые нужно удалить
4. Начать проектировать Backend API
```

Можно начинать прямо с этого.