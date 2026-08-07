-- Phase 5: Admin Messages
-- Bot "Admin ga xabar" tizimi — user messages to admin (registration + inbox)
-- Model: app/models/admin_message.py → AdminMessage

CREATE TABLE IF NOT EXISTS admin_messages (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    user_telegram_id BIGINT,
    user_name VARCHAR(255),
    content_type VARCHAR(20) DEFAULT 'text',
    text TEXT,
    file_id VARCHAR(255),
    is_read BOOLEAN DEFAULT FALSE,
    is_replied BOOLEAN DEFAULT FALSE,
    admin_reply TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_admin_messages_user_id ON admin_messages(user_id);
CREATE INDEX IF NOT EXISTS idx_admin_messages_user_telegram_id ON admin_messages(user_telegram_id);
CREATE INDEX IF NOT EXISTS idx_admin_messages_created_at ON admin_messages(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_admin_messages_is_read ON admin_messages(is_read);