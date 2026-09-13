# 📁 MyestroEco — To'liq File/Folder Arxitekturasi

**Asosiy papka:** `c:\Projects\MyestroEco\MyestroEco\`

> Eslatma: `node_modules/`, `.venv/`, `.next/`, `__pycache__/`, `.git/` avtomatik generatsiya qilingan papkalar — ular arxitekturada ko'rsatilmagan.

```
📁 MyestroEco/
│
├── 📄 .env                              # Sekretlar (gitignore'da)
├── 📄 .gitignore
├── 📄 backend_logs.txt                  # Backend log fayli
├── 📄 docker-compose.yml                # 6 servis: postgres, redis, backend, bot, admin, exam
├── 📄 Dockerfile                        # (legacy) Telegram bot uchun
├── 📄 migrate.py                        # Migratsiya yordamchi skripti
├── 📄 package-lock.json
├── 📄 Procfile                          # Railway: worker = python -m bot.main
├── 📄 README.md                         # Loyiha umumiy obzori
├── 📄 run_alembic.py                    # Alembic ishga tushiruvchi
├── 📄 run_migrations.ps1                # Windows migratsiya skripti
├── 📄 setup_summary.py                  # Setup xulosasi skripti
├── 📄 start.sh                          # Botni ishga tushirish
├── 📄 temp.txt
├── 📄 "Your paragraph text-compressed.md"
│
├── 📁 .github/
│   └── 📁 workflows/
│       └── 📄 deploy.yml                # CI/CD (SSH deploy + alembic upgrade)
│
├── 📁 .vscode/
│   └── 📄 settings.json
│
├── 📁 knowledge/                        # (root) — bo'sh
│   └── 📁 grammar_chunks/               # (bo'sh papka)
│
├── 📁 admin/                            # ═══ Next.js 14 — Admin Panel ═══
│   ├── 📄 .dockerignore
│   ├── 📄 .eslintrc.json
│   ├── 📄 .gitignore
│   ├── 📄 Dockerfile
│   ├── 📄 next-env.d.ts
│   ├── 📄 next.config.js
│   ├── 📄 package.json
│   ├── 📄 postcss.config.js
│   ├── 📄 README.md
│   ├── 📄 tailwind.config.ts
│   ├── 📄 tsconfig.json
│   │
│   ├── 📁 app/
│   │   ├── 📄 layout.tsx
│   │   ├── 📄 page.tsx
│   │   ├── 📄 globals.css
│   │   ├── 📁 api/                      # Proxy routes (backend'ga)
│   │   │   ├── 📁 auth/
│   │   │   │   ├── 📁 login/            → 📄 route.ts
│   │   │   │   └── 📁 refresh/          → 📄 route.ts
│   │   │   ├── 📁 bot-texts/
│   │   │   │   ├── 📄 route.ts
│   │   │   │   ├── 📁 [id]/             → 📄 route.ts
│   │   │   │   ├── 📁 keys/             → 📄 route.ts
│   │   │   │   └── 📁 stats/            → 📄 route.ts
│   │   │   ├── 📁 broadcast/
│   │   │   │   ├── 📄 route.ts
│   │   │   │   ├── 📁 [id]/             → 📄 route.ts
│   │   │   │   ├── 📁 history/          → 📄 route.ts
│   │   │   │   ├── 📁 placeholders/     → 📄 route.ts
│   │   │   │   └── 📁 upload/           → 📄 route.ts
│   │   │   ├── 📁 content/              → 📄 route.ts
│   │   │   ├── 📁 contents/
│   │   │   │   └── 📁 [id]/             → 📄 route.ts
│   │   │   ├── 📁 inbox/
│   │   │   │   ├── 📁 messages/         → 📄 route.ts
│   │   │   │   └── 📁 messages/[...id]/ → 📄 route.ts
│   │   │   ├── 📁 tests/
│   │   │   │   ├── 📄 route.ts
│   │   │   │   └── 📁 [id]/
│   │   │   │       ├── 📄 route.ts
│   │   │   │       └── 📁 questions/
│   │   │   │           ├── 📄 route.ts
│   │   │   │           └── 📁 [qid]/    → 📄 route.ts
│   │   │   └── 📁 users/                → 📄 route.ts
│   │   │
│   │   ├── 📁 login/      📄 page.tsx
│   │   ├── 📁 dashboard/  📄 page.tsx + layout.tsx
│   │   ├── 📁 users/      📄 page.tsx + layout.tsx
│   │   ├── 📁 broadcast/  📄 page.tsx + layout.tsx
│   │   ├── 📁 bot-texts/  📄 page.tsx + layout.tsx
│   │   ├── 📁 content/    📄 page.tsx + layout.tsx
│   │   ├── 📁 inbox/      📄 page.tsx + layout.tsx
│   │   ├── 📁 tests/
│   │   │   ├── 📄 page.tsx  📄 layout.tsx
│   │   │   ├── 📁 [id]/     → 📄 page.tsx
│   │   │   └── 📁 import/   → 📄 page.tsx
│   │   └── 📁 exam/         # Imtihon boshqaruvi
│   │       ├── 📄 page.tsx  📄 layout.tsx
│   │       ├── 📁 create/      → 📄 page.tsx
│   │       ├── 📁 bulk-import/ → 📄 page.tsx
│   │       ├── 📁 exams/       → 📄 page.tsx
│   │       │   └── 📁 [id]/
│   │       │       ├── 📄 page.tsx
│   │       │       └── 📁 blocks/[blockId]/
│   │       │           ├── 📄 page.tsx
│   │       │           └── 📁 items/[itemId]/ → 📄 page.tsx
│   │       └── 📁 components/  → 📄 AudioUpload.tsx
│   │
│   ├── 📁 components/
│   │   ├── 📄 AuthGuard.tsx
│   │   ├── 📁 broadcast/    AudienceSelector, MediaUploader, PlaceholderHints (.tsx)
│   │   ├── 📁 chat/         chatThreads.tsx
│   │   ├── 📁 common/       EmptyState, ErrorDisplay, LoadingSpinner, Skeleton (.tsx)
│   │   ├── 📁 content/      ContentTable, EditContentModal (.tsx)
│   │   ├── 📁 dashboard/    ActivityChart, AiJobsStatus, CEFRPieChart,
│   │   │                   QuickActions.jsx, RecentAttempts, StatsCard (.tsx)
│   │   ├── 📁 layout/       Header, MobileSidebar, Sidebar (.tsx)
│   │   ├── 📁 tests/        DeleteConfirmModal, QuestionFormModal, QuestionList,
│   │   │                   TestFormModal, TestInfoCard, TestListTable (.tsx)
│   │   ├── 📁 text/         BotTextsTable.tsx
│   │   ├── 📁 ui/           Badge, Button, Card, ConfirmDialog, Dialog, Input (.tsx)
│   │   └── 📁 users/        DirectMessage, UserDetailModal, UserEditForm, UserTable (.tsx)
│   │
│   ├── 📁 context/    → 📄 AuthContext.tsx
│   ├── 📁 hooks/      → useAudienceSelection, useContent, useDashboard,
│   │                  useInboxWebSocket, useUsers (.ts)
│   ├── 📁 lib/        → api_client.ts, api.ts, broadcasttypes.ts, types.ts, utils.ts
│   ├── 📁 providers/  → 📄 QueryProvider.tsx
│   └── 📁 types/      → 📄 test.ts
~
│
├── 📁 exam/                              # ═══ Next.js 14 — Landing + Exam ═══
│   ├── 📄 .dockerignore
│   ├── 📄 .env
│   ├── 📄 Dockerfile
│   ├── 📄 jsconfig.json
│   ├── 📄 middleware.ts
│   ├── 📄 next-env.d.ts
│   ├── 📄 next.config.js
│   ├── 📄 package.json
│   ├── 📄 postcss.config.js
│   ├── 📄 tailwind.config.js / .ts
│   ├── 📄 tsconfig.json
│   │
│   ├── 📁 app/
│   │   ├── 📄 layout.tsx
│   │   ├── 📄 page.tsx                   # Landing sahifasi
│   │   ├── 📄 globals.css
│   │   ├── 📄 providers.tsx
│   │   ├── 📁 login/      → 📄 page.tsx
│   │   ├── 📁 cabinet/    → 📄 page.tsx
│   │   ├── 📁 exams/
│   │   │   ├── 📄 page.tsx
│   │   │   ├── 📁 [attemptId]/      → 📄 page.tsx
│   │   │   └── 📁 results/
│   │   │       ├── 📄 page.tsx
│   │   │       └── 📁 [attemptId]/  → 📄 page.tsx
│   │   │
│   ├── 📁 components/
│   │   ├── 📄 AudioPlayer.tsx
│   │   ├── 📁 auth/         → 📄 TelegramLogin.tsx
│   │   ├── 📁 exam/
│   │   │   ├── 📄 OptionButton.tsx
│   │   │   ├── 📄 QuestionCard.tsx
│   │   │   ├── 📄 WritingResult.tsx
│   │   │   ├── 📁 reading/   → 📄 ReadingPassage.tsx
│   │   │   ├── 📁 speaking/  → 📄 SpeakingRecorder.tsx
│   │   │   └── 📁 writing/   → 📄 WritingEditor.tsx
│   │   ├── 📁 hooks/         → 📄 useTelegramWebApp.ts
│   │   └── 📁 landing/       → Aurora, AuroraController, CurtaineEffect, FAQ,
│   │                         Footer, Header, interactiveDemo, LearningJourney,
│   │                         MethodSection, Sections (.tsx)
│   │
│   ├── 📁 lib/        → 📄 api.ts
│   └── 📁 public/     → 📄 favicon.ico, 📄 logo.png
│
├── 📁 telegram_bot/                      # ═══ Python Monorepo ═══
│   ├── 📄 requirements.txt
│   ├── 📄 add_channel_required.py
│   ├── 📄 convert_pdf_to_rag.py
│   ├── 📄 split_grammar_book.py
│   │
│   ├── 📁 shared/                        # Umumiy modul
│   │   ├── 📄 __init__.py
│   │   ├── 📄 ai_client.py               # OpenRouter AI client
│   │   └── 📄 json_logger.py
│   │
│   ├── 📁 backend/                       # ═══ FastAPI REST API (v2.1.0) ═══
│   │   ├── 📄 alembic.ini
│   │   ├── 📄 Dockerfile
│   │   ├── 📄 requirements.txt
│   │   ├── 📄 run_migration.py
│   │   ├── 📁 app/
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 main.py                # FastAPI ilova yig'ilishi
│   │   │   ├── 📄 config.py              # Pydantic settings
│   │   │   ├── 📄 database.py            # SQLAlchemy async session
│   │   │   ├── 📁 api/                   # Router'lar
│   │   │   │   ├── 📄 __init__.py
│   │   │   │   ├── 📄 admin.py
│   │   │   │   ├── 📄 admin_messages.py
│   │   │   │   ├── 📄 ai_assistant.py
│   │   │   │   ├── 📄 auth.py
│   │   │   │   ├── 📄 bot_text.py
│   │   │   │   ├── 📄 broadcast.py
│   │   │   │   ├── 📄 content.py
│   │   │   │   ├── 📄 inbox.py
│   │   │   │   ├── 📄 knowledge.py
│   │   │   │   ├── 📄 logs.py
│   │   │   │   ├── 📄 settings.py
│   │   │   │   ├── 📄 stats.py
│   │   │   │   ├── 📄 sync.py
│   │   │   │   ├── 📄 tests.py
│   │   │   │   ├── 📄 tests_import.py
│   │   │   │   ├── 📄 users.py
│   │   │   │   └── 📁 exam_v2/           # Imtihon API (prefix: /api/v2/exam)
│   │   │   │       ├── 📄 __init__.py
│   │   │   │       ├── 📄 router.py      # exam_v2 router yig'ilishi
│   │   │   │       ├── 📄 auth.py        # Telegram auth
│   │   │   │       ├── 📄 exams.py
│   │   │   │       ├── 📄 attempts.py
│   │   │   │       ├── 📄 answers.py
│   │   │   │       ├── 📄 admin.py
│   │   │   │       ├── 📄 media.py
│   │   │   │       └── 📄 admin_import.py
│   │   │   ├── 📁 core/
│   │   │   │   ├── 📄 __init__.py
│   │   │   │   ├── 📄 security.py        # JWT, bcrypt
│   │   │   │   ├── 📄 deps.py            # Dependency'lar
│   │   │   │   ├── 📄 exceptions.py      # AppException
│   │   │   │   └── 📄 session_deps.py
│   │   │   ├── 📁 models/                # SQLAlchemy modellar
│   │   │   │   ├── 📄 __init__.py
│   │   │   │   ├── 📄 user.py
│   │   │   │   ├── 📄 conversation.py
│   │   │   │   ├── 📄 ai_memory.py
│   │   │   │   ├── 📄 bot_text.py
│   │   │   │   ├── 📄 broadcast.py
│   │   │   │   ├── 📄 content.py
│   │   │   │   ├── 📄 exam.py  📄 exam_enums.py
│   │   │   │   ├── 📄 inbox.py
│   │   │   │   ├── 📄 knowledge.py
│   │   │   │   ├── 📄 logs.py
│   │   │   │   ├── 📄 settings.py
│   │   │   │   ├── 📄 tests.py
│   │   │   │   └── 📄 admin_message.py
│   │   │   ├── 📁 schemas/               # Pydantic sxemalar
│   │   │   │   ├── 📄 __init__.py
│   │   │   │   ├── 📄 user.py  📄 phone.py
│   │   │   │   ├── 📄 conversation.py  📄 chat_context.py
│   │   │   │   ├── 📄 bot_text.py  📄 broadcast.py
│   │   │   │   ├── 📄 content.py  📄 knowledge.py
│   │   │   │   ├── 📄 stats.py  📄 admin_message.py
│   │   │   │   ├── 📄 tests_import.py  📄 exam.py  📄 exam_import.py
│   │   │   ├── 📁 services/              # Biznes-logika
│   │   │   │   ├── 📄 __init__.py
│   │   │   │   ├── 📄 auth_service.py
│   │   │   │   ├── 📄 session_service.py
│   │   │   │   ├── 📄 ai_service.py
│   │   │   │   ├── 📄 ai_memory_service.py
│   │   │   │   ├── 📄 knowledge_service.py
│   │   │   │   ├── 📄 inbox_listener.py
│   │   │   │   ├── 📄 placeholder_registry.py
│   │   │   │   ├── 📄 telegram_auth_service.py
│   │   │   │   ├── 📄 telegram_webapp_service.py
│   │   │   │   ├── 📄 tests_import_service.py
│   │   │   │   ├── 📄 exam_ai_service.py
│   │   │   │   ├── 📄 exam_import_service.py
│   │   │   │   ├── 📄 exam_scoring_service.py
│   │   │   │   └── 📁 exam/
│   │   │   │       ├── 📄 __init__.py
│   │   │   │       ├── 📄 media_servicea.py
│   │   │   │       ├── 📄 telegram_auth_service.py
│   │   │   │       └── 📄 transcription_service.py
│   │   │   └── 📁 websocket/
│   │   │       ├── 📄 __init__.py
│   │   │       └── 📄 admin_ws.py        # /ws/admin realtime
│   │   ├── 📁 migrations/                # Alembic
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 env.py
│   │   │   ├── 📄 script.py.mako
│   │   │   ├── 📄 tests_tables.sql
│   │   │   └── 📁 versions/
│   │   │       ├── 📄 001_add_tests_tables.py
│   │   │       └── 📄 002_add_bot_texts_table.py
│   │   ├── ⚠️ 📁 "migrations copy"/      # Keraksiz dublikat papka
│   │   │   └── 📄 env.py
│   │   └── 📁 scripts/
│   │       ├── 📄 create_admin.py
│   │       ├── 📄 set_admin_password.py
│   │       ├── 📄 seed_bot_texts.py
│   │       ├── 📄 seed_content.py
│   │       ├── 📄 migrate.py
│   │       ├── 📄 migrate_tests.py
│   │       ├── 📄 run_migrations.py
│   │       └── 📄 start_backend.sh
│   │
│   ├── 📁 bot/                           # ═══ aiogram 3.30 Bot ═══
│   │   ├── 📄 main.py                    # Bot yig'ilishi (polling + worker'lar)
│   │   ├── 📄 config.py
│   │   ├── 📄 database.py
│   │   ├── 📄 Dockerfile
│   │   ├── 📄 requirements.txt
│   │   ├── 📁 handlers/
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 start.py  📄 register.py  📄 profile.py
│   │   │   ├── 📄 menu.py  📄 contact.py  📄 debug.py
│   │   │   ├── 📄 ai_agent.py  📄 voice.py  📄 messages.py
│   │   │   ├── 📄 test_quiz.py
│   │   │   ├── 📄 inbox.py  📄 broadcast.py
│   │   │   ├── 📄 reminders.py  📄 referral.py  📄 academy.py
│   │   │   ├── 📄 admin.py
│   │   │   ├── 📄 photo.py  📄 document.py  📄 sticker.py  📄 video.py
│   │   │   └── 📄 errors.py
│   │   ├── 📁 keyboards/
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 reply.py  📄 inline.py  📄 inline_temp.py  📄 extended_buttons.py
│   │   ├── 📁 middlewares/
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 db_session.py      # DB sessiya
│   │   │   ├── 📄 bot_guard.py       # Botlarni bloklash
│   │   │   ├── 📄 channel_check.py   # Kanal obunasi tekshiruvi
│   │   │   └── 📄 ai_guard.py        # AI rejimi nazorati
│   │   ├── 📁 services/
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 ai_service.py          # OpenRouter streaming
│   │   │   ├── 📄 broadcast_worker.py    # Broadcast queue
│   │   │   └── 📄 content_uploader.py
│   │   ├── 📁 states/
│   │   │   ├── 📄 registration.py
│   │   │   ├── 📄 registrations_filter.py
│   │   │   └── 📄 test_states.py
│   │   ├── 📁 utils/
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 api_client.py  📄 ai_client.py  📄 ai_context.py
│   │   │   ├── 📄 ai_memory_client.py  📄 rag_client.py
│   │   │   ├── 📄 ai_prompts.py  📄 ai_prompts_enhanced.py
│   │   │   ├── 📄 text_cache.py  📄 i18n.py  📄 helpers.py  📄 redis_client.py
│   │   ├── 📁 workers/
│   │   │   └── 📄 inbox_delivery.py      # Fon worker (asyncio task)
│   │   └── ⚠️ 📁 bot/                    # Dublikat ichki papka
│   │       └── 📁 utils/ → 📄 i18n.py
│   │
│   └── 📁 knowledge/                     # ═══ RAG bilimlar bazasi ═══
│       ├── 📄 _index.yaml                # Kategoriya indeksi
│       ├── 📄 about_us.md  📄 platform_guide.md
│       ├── 📄 cefr_levels.md  📄 english_tips.md
│       ├── 📄 grammar_basics.md  📄 faq.md  📄 EssentialWords.md
│       ├── 📄 split_book_rag.py
│       ├── 📁 grammar_chunks/            # 31 fayl: unit_91..114 + appendix_1..6 + intro
│       ├── 📁 pdfs/                      # 📄 EssentialWords.pdf, "Your paragraph text-compressed.pdf"
│       └── 📁 src/                       # unit_88, 91..113 manba fayllari
│
├── 📁 migrations/                        # ═══ SQL sxema (root) ═══
│   ├── 📄 init.sql                       # 14+ jadval + default admin
│   ├── 📄 README.md
│   ├── 📄 run_migrations.sh
│   ├── 📄 run_migrations.bat
│   └── 📁 versions/
│       ├── 📄 000_create_schema_migrations.sql
│       ├── 📄 001_drop_old_exam_tables.sql
│       ├── 📄 002_create_new_exam_tables.sql
│       ├── 📄 003_add_user_preferences.sql
│       ├── 📄 004_phone_password_auth.sql
│       ├── 📄 005_test_table.sql
│       ├── 📄 006_questions.sql
│       ├── 📄 007_correct_question.sql
│       ├── 📄 008_add_exam.sql
│       └── 📄 009_speaking_exam_system.sql
│
└── 📁 scripts/
    └── 📄 migrate_sql.py
```

---

## 📊 Qisqacha statistika

| Komponent | Tavsif | Hajm |
|---|---|---|
| **admin/** | Next.js 14 admin panel — 18 ta proxy API route, 40+ komponent | Frontend |
| **exam/** | Next.js 14 landing + imtihon (login, cabinet, exams, results) | Frontend |
| **telegram_bot/backend/** | FastAPI 2.1.0 — 20+ router, 15+ model, 16 service, WebSocket | Backend |
| **telegram_bot/bot/** | aiogram 3.30 — 22 handler, 4 middleware, 2 worker, Redis FSM | Bot |
| **telegram_bot/shared/** | ai_client + json_logger | Umumiy modul |
| **telegram_bot/knowledge/** | RAG — 7 asosiy .md + 31 grammatika chunk + 2 PDF | Bilim bazasi |
| **migrations/** | init.sql + 10 SQL versiya (000–009) | DB sxema |

**Topilgan anomaliyalar (arxitekturada e'tibor qiling):**
- ⚠️ `telegram_bot/backend/migrations copy/` — `migrations/` dublikati (keraksiz)
- ⚠️ `telegram_bot/bot/bot/utils/i18n.py` — `bot/utils/i18n.py` dublikati
- ⚠️ Root `knowledge/grammar_chunks/` — bo'sh papka (asosiy bilim bazasi `telegram_bot/knowledge/` da)