-- Reminder tizimi uchun jadval
CREATE TABLE IF NOT EXISTS reminders (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    reminder_type VARCHAR(20) NOT NULL DEFAULT 'once',
    due_at TIMESTAMP WITH TIME ZONE NOT NULL,
    scheduled_time VARCHAR(5),
    day_of_week INTEGER,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    last_sent_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indeks: Worker tez ishlashi uchun
CREATE INDEX IF NOT EXISTS idx_reminders_due_active 
    ON reminders(is_active, due_at) 
    WHERE is_active = TRUE;

CREATE INDEX IF NOT EXISTS idx_reminders_user 
    ON reminders(user_id);

-- updated_at trigger
DROP TRIGGER IF EXISTS trg_reminders_updated_at ON reminders;

CREATE OR REPLACE FUNCTION update_reminders_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_reminders_updated_at
    BEFORE UPDATE ON reminders
    FOR EACH ROW
    EXECUTE FUNCTION update_reminders_updated_at();