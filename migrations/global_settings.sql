-- Phase 5: Global Settings
-- Control global bot and AI features across entire platform

CREATE TABLE IF NOT EXISTS global_settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(50) UNIQUE NOT NULL,
    value VARCHAR(255),
    description TEXT,
    updated_by BIGINT REFERENCES users(id) ON DELETE SET NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Initial settings
INSERT INTO global_settings (key, value, description) VALUES
('BOT_ENABLED', 'true', 'Enable/disable entire Telegram bot for all users except admins'),
('AI_ENABLED', 'true', 'Enable/disable AI responses for all users except admins');

CREATE INDEX IF NOT EXISTS idx_global_settings_key ON global_settings(key);
