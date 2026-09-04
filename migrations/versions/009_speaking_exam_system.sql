-- exam_items ga yangi ustunlar
ALTER TABLE exam_items ADD COLUMN IF NOT EXISTS 
  follow_up_questions JSONB DEFAULT '[]'::jsonb;
-- Speaking uchun: asosiy savol + qo'shimcha savollar (Part 3 style)

-- exam_answers ga audio metadata
ALTER TABLE exam_answers ADD COLUMN IF NOT EXISTS audio_duration_ms INTEGER;
ALTER TABLE exam_answers ADD COLUMN IF NOT EXISTS audio_format VARCHAR(20);
ALTER TABLE exam_answers ADD COLUMN IF NOT EXISTS word_count INTEGER;
ALTER TABLE exam_answers ADD COLUMN IF NOT EXISTS pause_count INTEGER;
ALTER TABLE exam_answers ADD COLUMN IF NOT EXISTS speaking_rate_wpm DECIMAL(5,2);
