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
ALTER COLUMN audio_file_id TYPE VARCHAR(255);


-- 1. Mavjud ma'lumotlarni tozalash (agar string bo'lsa)
UPDATE exam_answers 
SET audio_file_id = NULL 
WHERE audio_file_id IS NOT NULL 
  AND audio_file_id::text !~ '^[0-9]+$';

-- 2. Ustun tipini INTEGER ga o'zgartirish
ALTER TABLE exam_answers 
ALTER COLUMN audio_file_id TYPE INTEGER 
USING CASE 
    WHEN audio_file_id IS NULL THEN NULL
    WHEN audio_file_id::text ~ '^[0-9]+$' THEN audio_file_id::text::INTEGER
    ELSE NULL
END;

    