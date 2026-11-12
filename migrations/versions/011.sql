-- Smart Reminder tizimi uchun yangi ustunlar
ALTER TABLE reminders 
    ADD COLUMN IF NOT EXISTS is_ai_generated BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE reminders 
    ADD COLUMN IF NOT EXISTS ai_prompt TEXT;

-- Indeks: AI reminderlar uchun
CREATE INDEX IF NOT EXISTS idx_reminders_ai_generated 
    ON reminders(is_ai_generated) 
    WHERE is_ai_generated = TRUE;

-- Izoh
COMMENT ON COLUMN reminders.is_ai_generated IS 'Agar TRUE bo''lsa, har safar AI yangi content generatsiya qiladi';
COMMENT ON COLUMN reminders.ai_prompt IS 'AI uchun prompt (masalan: "B1 daraja uchun 10 ta yangi so''z yubor")';


ALTER TABLE exam_answers
ADD COLUMN IF NOT EXISTS audio_file_id VARCHAR(255);
