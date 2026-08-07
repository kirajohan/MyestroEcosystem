-- ============================================================
-- Myestro Initial Schema
-- 14 tables (ENUM types o'chirilgan — barcha ENUM lar VARCHAR sifatida ishlatiladi)
-- Idempotent: all CREATE TABLE/INDEX use IF NOT EXISTS
-- ============================================================

-- -----------------------------------------------------------
-- 1. users
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id              BIGSERIAL PRIMARY KEY,
    email           VARCHAR(255) UNIQUE,
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
    deleted_at      TIMESTAMPTZ,
    updated_at      TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- -----------------------------------------------------------
-- 2. sessions
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS sessions (
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

CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at);

-- -----------------------------------------------------------
-- 3. conversation_threads
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS conversation_threads (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    telegram_topic_id BIGINT NOT NULL UNIQUE,
    topic_title VARCHAR(255),
    cefr_level VARCHAR(10) DEFAULT 'A1',
    is_active BOOLEAN DEFAULT TRUE,
    last_message_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT idx_thread_user_active UNIQUE(user_id, is_active)
);

CREATE INDEX IF NOT EXISTS idx_threads_user_id ON conversation_threads(user_id);
CREATE INDEX IF NOT EXISTS idx_threads_last_message ON conversation_threads(last_message_at DESC);

-- -----------------------------------------------------------
-- 4. messages
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS messages (
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

CREATE INDEX IF NOT EXISTS idx_messages_thread_id ON messages(thread_id);
CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);

-- -----------------------------------------------------------
-- 10. knowledge_categories
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS knowledge_categories (
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
CREATE TABLE IF NOT EXISTS knowledge_docs (
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

CREATE INDEX IF NOT EXISTS idx_knowledge_docs_category_id ON knowledge_docs(category_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_docs_cefr_level ON knowledge_docs(cefr_level);

-- -----------------------------------------------------------
-- 12. api_logs
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS api_logs (
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

CREATE INDEX IF NOT EXISTS idx_api_logs_user_id ON api_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_api_logs_created_at ON api_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_api_logs_endpoint ON api_logs(endpoint);

-- -----------------------------------------------------------
-- 13. error_logs
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS error_logs (
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

CREATE INDEX IF NOT EXISTS idx_error_logs_service ON error_logs(service);
CREATE INDEX IF NOT EXISTS idx_error_logs_severity ON error_logs(severity);
CREATE INDEX IF NOT EXISTS idx_error_logs_is_fixed ON error_logs(is_fixed);
CREATE INDEX IF NOT EXISTS idx_error_logs_created_at ON error_logs(created_at);

-- -----------------------------------------------------------
-- 14. audit_logs
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS audit_logs (
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

CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);

-- -----------------------------------------------------------
-- 15. system_settings
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS system_settings (
    id              BIGSERIAL PRIMARY KEY,
    key             VARCHAR(255) NOT NULL UNIQUE,
    value           TEXT NOT NULL,
    description     TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at      TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_system_settings_key ON system_settings(key);

-- -----------------------------------------------------------
-- 16. content_items (Video / File / Text lessons)
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS content_items (
    id              BIGSERIAL PRIMARY KEY,
    title           VARCHAR(255) NOT NULL,
    description     TEXT,
    content_type    VARCHAR(20) NOT NULL,
    file_path       TEXT,
    telegram_file_id VARCHAR(255),
    cefr_level      VARCHAR(10),
    order_index     INTEGER DEFAULT 0,
    is_active       BOOLEAN DEFAULT TRUE NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at      TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_content_items_type ON content_items(content_type);
CREATE INDEX IF NOT EXISTS idx_content_items_cefr ON content_items(cefr_level);
CREATE INDEX IF NOT EXISTS idx_content_items_active ON content_items(is_active);

-- -----------------------------------------------------------
-- 17. bot_texts (CMS for bot messages)
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS bot_texts (
    id              BIGSERIAL PRIMARY KEY,
    key             VARCHAR(100) NOT NULL,
    lang            VARCHAR(10) DEFAULT 'uz' NOT NULL,
    text            TEXT NOT NULL,
    updated_at      TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_bot_texts_key ON bot_texts(key);
CREATE INDEX IF NOT EXISTS idx_bot_texts_lang ON bot_texts(lang);

-- -----------------------------------------------------------
-- 18. inbox_messages (Admin Inbox for user messages)
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS inbox_messages (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    subject VARCHAR(255),
    user_message TEXT NOT NULL,
    admin_reply TEXT,
    admin_id INTEGER,
    status VARCHAR(50) DEFAULT 'new',
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_inbox_messages_user_id ON inbox_messages(user_id);
CREATE INDEX IF NOT EXISTS idx_inbox_messages_status ON inbox_messages(status);
CREATE INDEX IF NOT EXISTS idx_inbox_messages_created_at ON inbox_messages(created_at);

-- -----------------------------------------------------------
-- 19. inbox_message_history
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS inbox_message_history (
    id SERIAL PRIMARY KEY,
    inbox_message_id INTEGER NOT NULL REFERENCES inbox_messages(id) ON DELETE CASCADE,
    sender_id INTEGER REFERENCES users(id),
    message_text TEXT NOT NULL,
    message_type VARCHAR(50) DEFAULT 'user_message',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_inbox_message_history_inbox_id ON inbox_message_history(inbox_message_id);
CREATE INDEX IF NOT EXISTS idx_inbox_message_history_created_at ON inbox_message_history(created_at);

-- -----------------------------------------------------------
-- 20. broadcast_jobs (Phase 3)
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS broadcast_jobs (
    id BIGSERIAL PRIMARY KEY,
    created_by_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    message_type VARCHAR(20) DEFAULT 'text',
    file_id VARCHAR(255),
    target_users BIGINT[] DEFAULT '{}',
    scheduled_at TIMESTAMPTZ DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    total_users INT DEFAULT 0,
    sent_count INT DEFAULT 0,
    error_count INT DEFAULT 0,
    error_message TEXT
);

CREATE INDEX IF NOT EXISTS idx_broadcast_jobs_status ON broadcast_jobs(status);
CREATE INDEX IF NOT EXISTS idx_broadcast_jobs_created_at ON broadcast_jobs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_broadcast_jobs_created_by ON broadcast_jobs(created_by_id);

-- -----------------------------------------------------------
-- 21. broadcast_history (Phase 3)
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS broadcast_history (
    id BIGSERIAL PRIMARY KEY,
    broadcast_job_id BIGINT NOT NULL REFERENCES broadcast_jobs(id) ON DELETE CASCADE,
    recipient_user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    message_telegram_id BIGINT,
    status VARCHAR(20) DEFAULT 'pending',
    error_message TEXT,
    sent_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_broadcast_history_job_id ON broadcast_history(broadcast_job_id);
CREATE INDEX IF NOT EXISTS idx_broadcast_history_recipient ON broadcast_history(recipient_user_id);
CREATE INDEX IF NOT EXISTS idx_broadcast_history_status ON broadcast_history(status);
CREATE INDEX IF NOT EXISTS idx_broadcast_history_created_at ON broadcast_history(created_at DESC);

-- ============================================================
-- DEFAULT ADMIN USER
-- ============================================================
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
    'admin123',
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