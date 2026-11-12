-- audio_file_id uuid hex string saqlaydi (MediaService.save_exam_audio), INTEGER emas.
-- Ustun hech bir migratsiyada yaratilmagan bo'lishi mumkin, yoki INTEGER bo'lishi mumkin.
ALTER TABLE exam_answers ADD COLUMN IF NOT EXISTS audio_file_id VARCHAR(255);
ALTER TABLE exam_answers
    ALTER COLUMN audio_file_id TYPE VARCHAR(255) USING audio_file_id::text;
