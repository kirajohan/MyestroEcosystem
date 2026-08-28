-- tests jadvaliga yangi ustunlar qo'shish
-- Sana: 2026-08-28
-- Sabab: SQLAlchemy modelida mavjud, lekin bazada yo'q ustunlar

-- 1. total_duration ustuni (daqiqa)
ALTER TABLE tests 
ADD COLUMN IF NOT EXISTS total_duration INTEGER NOT NULL DEFAULT 30;

-- 2. max_score ustuni (maksimal ball)
ALTER TABLE tests 
ADD COLUMN IF NOT EXISTS max_score INTEGER;

-- 3. status ustuni (draft, published, active, archived)
ALTER TABLE tests 
ADD COLUMN IF NOT EXISTS status VARCHAR(50) NOT NULL DEFAULT 'active';

-- Mavjud yozuvlar uchun status ni 'active' ga o'rnatish (agar NULL bo'lsa)
UPDATE tests 
SET status = 'active' 
WHERE status IS NULL;

-- Indeks qo'shish (tezroq so'rovlar uchun)
CREATE INDEX IF NOT EXISTS idx_tests_status ON tests(status);
CREATE INDEX IF NOT EXISTS idx_tests_cefr_level ON tests(cefr_level);
CREATE INDEX IF NOT EXISTS idx_tests_is_active ON tests(is_active);