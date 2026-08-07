-- Phase 4: Inbox System
-- Admin inbox for receiving user messages and sending replies

CREATE TABLE IF NOT EXISTS inbox_messages (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    admin_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    subject VARCHAR(255),
    user_message TEXT NOT NULL,
    admin_reply TEXT,
    status VARCHAR(20) DEFAULT 'new',  -- 'new', 'read', 'replied', 'closed'
    is_read BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS inbox_message_history (
    id BIGSERIAL PRIMARY KEY,
    inbox_message_id BIGINT NOT NULL REFERENCES inbox_messages(id) ON DELETE CASCADE,
    sender_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    message_text TEXT NOT NULL,
    message_type VARCHAR(20) DEFAULT 'reply',  -- 'user_message', 'admin_reply'
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_inbox_user_status ON inbox_messages(user_id, status);
CREATE INDEX IF NOT EXISTS idx_inbox_created_at ON inbox_messages(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_inbox_history_message ON inbox_message_history(inbox_message_id);
