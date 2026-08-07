-- Phase 3: Broadcast System Tables
-- Contains jobs queue and delivery history

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

CREATE INDEX IF NOT EXISTS idx_broadcast_jobs_status ON broadcast_jobs(status);
CREATE INDEX IF NOT EXISTS idx_broadcast_jobs_created_at ON broadcast_jobs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_broadcast_jobs_created_by ON broadcast_jobs(created_by_id);
CREATE INDEX IF NOT EXISTS idx_broadcast_history_job_id ON broadcast_history(broadcast_job_id);
CREATE INDEX IF NOT EXISTS idx_broadcast_history_recipient ON broadcast_history(recipient_user_id);
CREATE INDEX IF NOT EXISTS idx_broadcast_history_status ON broadcast_history(status);
CREATE INDEX IF NOT EXISTS idx_broadcast_history_created_at ON broadcast_history(created_at DESC);
