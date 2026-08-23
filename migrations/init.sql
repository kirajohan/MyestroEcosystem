-- ============================================================
-- Myestro Initial Schema
-- 14 tables (ENUM types o'chirilgan — barcha ENUM lar VARCHAR sifatida ishlatiladi)
-- ============================================================

-- -----------------------------------------------------------
-- 1. users
-- -----------------------------------------------------------
CREATE TABLE users (
    id              BIGSERIAL PRIMARY KEY,
    email           VARCHAR(255) NOT NULL UNIQUE,
    password_hash   VARCHAR(255),   
    full_name       VARCHAR(255) NOT NULL,
    role            VARCHAR(20) DEFAULT 'student' NOT NULL,
    cefr_level      VARCHAR(10) DEFAULT 'A1' NOT NULL,
    target_level    VARCHAR(10) DEFAULT 'B1' NOT NULL,
    avatar_url      TEXT,
    phone           VARCHAR(50),
    lang            VARCHAR(10) DEFAULT 'uz' NOT NULL,
    learning_lang   VARCHAR(10) DEFAULT 'en' NOT NULL,
    telegram_id     BIGINT UNIQUE,
    telegram_username VARCHAR(255),
    auth_provider   VARCHAR(20) DEFAULT 'email' NOT NULL,
    provider_user_id VARCHAR(255),
    is_active       BOOLEAN DEFAULT TRUE NOT NULL,
    is_verified     BOOLEAN DEFAULT FALSE NOT NULL,
    profile_completed BOOLEAN DEFAULT FALSE NOT NULL,
    last_login_at   TIMESTAMPTZ,
    location        VARCHAR(255),
    ai_enabled      BOOLEAN DEFAULT TRUE NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at      TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    deleted_at      TIMESTAMPTZ
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_telegram_id ON users(telegram_id);
CREATE INDEX idx_users_role ON users(role);

-- -----------------------------------------------------------
-- 2. sessions
-- -----------------------------------------------------------
CREATE TABLE sessions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    refresh_token   VARCHAR(500) NOT NULL,
    device_info     TEXT,
    ip_address      VARCHAR(45),
    expires_at      TIMESTAMPTZ NOT NULL,
    is_revoked      BOOLEAN DEFAULT FALSE NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    revoked_at      TIMESTAMPTZ
);

CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_expires_at ON sessions(expires_at);

-- -----------------------------------------------------------
-- 3. conversation_threads
-- -----------------------------------------------------------
CREATE TABLE conversation_threads (
    id                  BIGSERIAL PRIMARY KEY,
    user_id             BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title               VARCHAR(255),
    cefr_level          VARCHAR(10) DEFAULT 'A1' NOT NULL,
    is_active           BOOLEAN DEFAULT TRUE NOT NULL,
    telegram_thread_id  BIGINT,
    last_sync_at        TIMESTAMPTZ,
    created_at          TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at          TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_conversation_threads_user_id ON conversation_threads(user_id);

-- -----------------------------------------------------------
-- 4. messages
-- -----------------------------------------------------------
CREATE TABLE messages (
    id                  BIGSERIAL PRIMARY KEY,
    thread_id           BIGINT NOT NULL REFERENCES conversation_threads(id) ON DELETE CASCADE,
    user_id             BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role                VARCHAR(20) DEFAULT 'user' NOT NULL,
    content             TEXT NOT NULL,
    content_type        VARCHAR(20) DEFAULT 'text' NOT NULL,
    ai_model            VARCHAR(100),
    tokens_used         INTEGER,
    processing_time_ms  INTEGER,
    cefr_level          VARCHAR(10),
    grammar_corrections JSONB,
    vocabulary_suggestions JSONB,
    source              VARCHAR(20) DEFAULT 'telegram' NOT NULL,
    created_at          TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_messages_thread_id ON messages(thread_id);
CREATE INDEX idx_messages_user_id ON messages(user_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);

-- -----------------------------------------------------------
-- 10. knowledge_categories
-- -----------------------------------------------------------
CREATE TABLE knowledge_categories (
    id          BIGSERIAL PRIMARY KEY,
    name        VARCHAR(255) NOT NULL,
    slug        VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    icon        VARCHAR(100),
    order_index INTEGER DEFAULT 0,
    is_active   BOOLEAN DEFAULT TRUE NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at  TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- -----------------------------------------------------------
-- 11. knowledge_docs
-- -----------------------------------------------------------
CREATE TABLE knowledge_docs (
    id          BIGSERIAL PRIMARY KEY,
    category_id BIGINT REFERENCES knowledge_categories(id) ON DELETE SET NULL,
    title       VARCHAR(255) NOT NULL,
    slug        VARCHAR(255) NOT NULL UNIQUE,
    file_path   TEXT NOT NULL,
    cefr_level  VARCHAR(10),
    description TEXT,
    tags        JSONB,
    is_active   BOOLEAN DEFAULT TRUE NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at  TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_knowledge_docs_category_id ON knowledge_docs(category_id);
CREATE INDEX idx_knowledge_docs_cefr_level ON knowledge_docs(cefr_level);


-- ══════════════════════════════════════════════════════════════
-- TESTS MODULE (Telegram Quiz Poll)
-- ══════════════════════════════════════════════════════════════

-- 1. tests jadvali
CREATE TABLE IF NOT EXISTS tests (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    cefr_level VARCHAR(2) NOT NULL,  -- A1, A2, B1, B2, C1, C2
    passing_score INTEGER NOT NULL DEFAULT 60,  -- Foiz (60%)
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_tests_cefr_level ON tests(cefr_level);
CREATE INDEX IF NOT EXISTS ix_tests_is_active ON tests(is_active);

-- 2. test_questions jadvali
CREATE TABLE IF NOT EXISTS test_questions (
    id SERIAL PRIMARY KEY,
    test_id INTEGER NOT NULL REFERENCES tests(id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    options JSONB NOT NULL,  -- ["variant1", "variant2", "variant3", "variant4"]
    correct_option_index INTEGER NOT NULL,  -- 0, 1, 2 yoki 3
    explanation TEXT,  -- Telegram quiz explanation
    order_index INTEGER NOT NULL DEFAULT 0,  -- Savol tartibi
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_test_questions_test_id ON test_questions(test_id);
CREATE INDEX IF NOT EXISTS ix_test_questions_order ON test_questions(test_id, order_index);

-- 3. test_attempts jadvali
CREATE TABLE IF NOT EXISTS test_attempts (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,  -- Telegram user ID
    test_id INTEGER NOT NULL REFERENCES tests(id) ON DELETE CASCADE,
    score INTEGER NOT NULL,  -- To'g'ri javoblar soni
    total_questions INTEGER NOT NULL,  -- Jami savollar
    percentage INTEGER NOT NULL,  -- Foiz (0-100)
    passed BOOLEAN NOT NULL,  -- Testdan o'tdi/o'tmadi
    finished_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_test_attempts_user_id ON test_attempts(user_id);
CREATE INDEX IF NOT EXISTS ix_test_attempts_test_id ON test_attempts(test_id);
CREATE INDEX IF NOT EXISTS ix_test_attempts_user_test ON test_attempts(user_id, test_id);

-- -----------------------------------------------------------
-- 12. api_logs
-- -----------------------------------------------------------
CREATE TABLE api_logs (
    id              BIGSERIAL PRIMARY KEY,
    user_id         BIGINT REFERENCES users(id) ON DELETE SET NULL,
    endpoint        VARCHAR(500) NOT NULL,
    method          VARCHAR(10) NOT NULL,
    status_code     INTEGER NOT NULL,
    response_time_ms INTEGER,
    ip_address      VARCHAR(45),
    user_agent      TEXT,
    request_body    JSONB,
    response_body   JSONB,
    created_at      TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_api_logs_user_id ON api_logs(user_id);
CREATE INDEX idx_api_logs_created_at ON api_logs(created_at);
CREATE INDEX idx_api_logs_endpoint ON api_logs(endpoint);

-- -----------------------------------------------------------
-- 13. error_logs
-- -----------------------------------------------------------
CREATE TABLE error_logs (
    id              BIGSERIAL PRIMARY KEY,
    service         VARCHAR(100) NOT NULL,
    error_type      VARCHAR(255) NOT NULL,
    error_message   TEXT NOT NULL,
    stack_trace     TEXT,
    cause           TEXT,
    solution        TEXT,
    is_fixed        BOOLEAN DEFAULT FALSE NOT NULL,
    severity        VARCHAR(20) DEFAULT 'error' NOT NULL,
    user_id         BIGINT REFERENCES users(id) ON DELETE SET NULL,
    metadata        JSONB,
    created_at      TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    fixed_at        TIMESTAMPTZ
);

CREATE INDEX idx_error_logs_service ON error_logs(service);
CREATE INDEX idx_error_logs_severity ON error_logs(severity);
CREATE INDEX idx_error_logs_is_fixed ON error_logs(is_fixed);
CREATE INDEX idx_error_logs_created_at ON error_logs(created_at);

-- -----------------------------------------------------------
-- 14. audit_logs
-- -----------------------------------------------------------
CREATE TABLE audit_logs (
    id              BIGSERIAL PRIMARY KEY,
    user_id         BIGINT REFERENCES users(id) ON DELETE SET NULL,
    action          VARCHAR(100) NOT NULL,
    resource        VARCHAR(255),
    details         JSONB,
    ip_address      VARCHAR(45),
    user_agent      TEXT,
    severity        VARCHAR(20) DEFAULT 'info' NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);

-- -----------------------------------------------------------
-- 15. system_settings
-- -----------------------------------------------------------
CREATE TABLE system_settings (
    id              BIGSERIAL PRIMARY KEY,
    key             VARCHAR(255) NOT NULL UNIQUE,
    value           TEXT NOT NULL,
    description     TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at      TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_system_settings_key ON system_settings(key);

-- -----------------------------------------------------------
-- 16. content_items (Video / File / Text lessons)
-- -----------------------------------------------------------
CREATE TABLE content_items (
    id              BIGSERIAL PRIMARY KEY,
    title           VARCHAR(255) NOT NULL,
    description     TEXT,
    content_type    VARCHAR(20) NOT NULL,  -- 'video' | 'file' | 'text'
    file_path       TEXT,
    telegram_file_id VARCHAR(255),
    cefr_level      VARCHAR(10),
    order_index     INTEGER DEFAULT 0,
    is_active       BOOLEAN DEFAULT TRUE NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at      TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_content_items_type ON content_items(content_type);
CREATE INDEX idx_content_items_cefr ON content_items(cefr_level);
CREATE INDEX idx_content_items_active ON content_items(is_active);

-- -----------------------------------------------------------
-- 17. bot_texts (CMS for bot messages)
-- -----------------------------------------------------------
CREATE TABLE bot_texts (
    id              BIGSERIAL PRIMARY KEY,
    key             VARCHAR(100) NOT NULL,
    lang            VARCHAR(10) DEFAULT 'uz' NOT NULL,
    text            TEXT NOT NULL,
    updated_at      TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_bot_texts_key ON bot_texts(key);
CREATE INDEX idx_bot_texts_lang ON bot_texts(lang);

-- -----------------------------------------------------------
-- 18. admin_messages (Inbox for user messages)
-- -----------------------------------------------------------
CREATE TABLE admin_messages (
    id              BIGSERIAL PRIMARY KEY,
    user_id         BIGINT REFERENCES users(id) ON DELETE SET NULL,
    user_telegram_id BIGINT,
    user_name       VARCHAR(255),
    content_type    VARCHAR(20) DEFAULT 'text' NOT NULL,  -- 'text' | 'photo' | 'voice' | 'document' | 'video' | 'sticker'
    text            TEXT,
    file_id         VARCHAR(255),
    is_read         BOOLEAN DEFAULT FALSE NOT NULL,
    is_replied      BOOLEAN DEFAULT FALSE NOT NULL,
    admin_reply     TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_admin_messages_user_id ON admin_messages(user_id);
CREATE INDEX idx_admin_messages_is_read ON admin_messages(is_read);
CREATE INDEX idx_admin_messages_created_at ON admin_messages(created_at);

-- -----------------------------------------------------------
-- 19. broadcast_jobs (Phase 3)
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS broadcast_jobs (
    id BIGSERIAL PRIMARY KEY,
    created_by_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,  -- HTML formatted
    message_type VARCHAR(20) DEFAULT 'text',  -- 'text', 'photo', 'video', 'document'
    file_id VARCHAR(255),  -- Telegram file_id for media
    target_users BIGINT[] DEFAULT '{}',  -- Array of user IDs (NULL or empty = all users)
    scheduled_at TIMESTAMPTZ DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'pending',  -- 'pending', 'queued', 'sending', 'completed', 'failed'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    total_users INT DEFAULT 0,
    sent_count INT DEFAULT 0,
    error_count INT DEFAULT 0,
    error_message TEXT
);

CREATE INDEX idx_broadcast_jobs_status ON broadcast_jobs(status);
CREATE INDEX idx_broadcast_jobs_created_at ON broadcast_jobs(created_at DESC);
CREATE INDEX idx_broadcast_jobs_created_by ON broadcast_jobs(created_by_id);

-- -----------------------------------------------------------
-- 20. broadcast_history (Phase 3)
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS broadcast_history (
    id BIGSERIAL PRIMARY KEY,
    broadcast_job_id BIGINT NOT NULL REFERENCES broadcast_jobs(id) ON DELETE CASCADE,
    recipient_user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    message_telegram_id BIGINT,  -- Telegram message ID if successfully sent
    status VARCHAR(20) DEFAULT 'pending',  -- 'pending', 'sent', 'failed'
    error_message TEXT,
    sent_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_broadcast_history_job_id ON broadcast_history(broadcast_job_id);
CREATE INDEX idx_broadcast_history_recipient ON broadcast_history(recipient_user_id);
CREATE INDEX idx_broadcast_history_status ON broadcast_history(status);
CREATE INDEX idx_broadcast_history_created_at ON broadcast_history(created_at DESC);


-- -----------------------------------------------------------
-- 21. ai_memory_sessions
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS ai_memory_sessions (
    id                  BIGSERIAL PRIMARY KEY,
    user_id             BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id          VARCHAR(255) UNIQUE,
    title               VARCHAR(255),
    language            VARCHAR(10) DEFAULT 'uz',
    cefr_level          VARCHAR(10) DEFAULT 'A1',
    created_at          TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    last_activity_at    TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    expires_at          TIMESTAMPTZ,
    message_count       INTEGER DEFAULT 0,
    is_active           BOOLEAN DEFAULT TRUE NOT NULL,
    context_summary     TEXT,
    summary_generated_at TIMESTAMPTZ
);

CREATE INDEX idx_ai_memory_sessions_user_id ON ai_memory_sessions(user_id);
CREATE INDEX idx_ai_memory_sessions_session_id ON ai_memory_sessions(session_id);

-- -----------------------------------------------------------
-- 22. ai_memory_messages
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS ai_memory_messages (
    id                  BIGSERIAL PRIMARY KEY,
    session_id          BIGINT NOT NULL REFERENCES ai_memory_sessions(id) ON DELETE CASCADE,
    user_id             BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role                VARCHAR(20) NOT NULL, -- 'user', 'assistant', 'system'
    content             TEXT NOT NULL,
    tokens_used         INTEGER,
    created_at          TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_ai_memory_messages_session_id ON ai_memory_messages(session_id);
CREATE INDEX idx_ai_memory_messages_user_id ON ai_memory_messages(user_id);

-- ============================================================
-- DEFAULT ADMIN USER
-- ============================================================
-- Email: admin@myestro.com
-- Password: admin123
-- Role: superadmin
INSERT INTO users (
    email,
    password_hash,
    full_name,
    role,
    cefr_level,
    target_level,
    lang,
    auth_provider,
    is_active,
    is_verified,
    profile_completed
) VALUES (
    'abdurakhmonbek0770@gmail.com',
    '$2b$12$Nq/aHl.C7F9jP1zR8mXq.O5K6T3wX7e8R9t0Y1u2V3w4X5y6Z7a8b', -- admin123 ning xeshi
    'Super Admin',
    'admin',
    'C2',
    'C2',
    'uz',
    'email',
    TRUE,
    TRUE,
    TRUE
)
ON CONFLICT (email) DO NOTHING;