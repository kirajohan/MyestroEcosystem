    -- test_questions jadvaliga yetishmayotgan ustunlarni qo'shish
    -- Sana: 2026-08-28
    -- Sabab: SQLAlchemy modelida mavjud, lekin bazada yo'q ustunlar

    -- 1. question_type (savol turi)
    ALTER TABLE test_questions 
    ADD COLUMN IF NOT EXISTS question_type VARCHAR(50) NOT NULL DEFAULT 'multiple_choice';

    -- 2. options (variantlar, JSONB formatida)
    ALTER TABLE test_questions 
    ADD COLUMN IF NOT EXISTS options JSONB NOT NULL DEFAULT '[]'::jsonb;

    -- 3. correct_answer (to'g'ri javob)
    ALTER TABLE test_questions 
    ADD COLUMN IF NOT EXISTS correct_answer VARCHAR(500) NOT NULL DEFAULT '';

    -- 4. explanation (tushuntirish)
    ALTER TABLE test_questions 
    ADD COLUMN IF NOT EXISTS explanation TEXT;

    -- 5. points (ball)
    ALTER TABLE test_questions 
    ADD COLUMN IF NOT EXISTS points INTEGER NOT NULL DEFAULT 1;
    -- Test_questions jadvalidan keraksiz va ziddiyatli ustunni o'chirish
    ALTER TABLE test_questions DROP COLUMN IF EXISTS correct_option_index;
    -- 6. difficulty (qiyinlik darajasi)
    ALTER TABLE test_questions 
    ADD COLUMN IF NOT EXISTS difficulty VARCHAR(20) NOT NULL DEFAULT 'medium';

    -- 7. order_index (tartib raqami)
    ALTER TABLE test_questions 
    ADD COLUMN IF NOT EXISTS order_index INTEGER NOT NULL DEFAULT 0;

    -- 8. created_at (yaratilgan vaqt)
    ALTER TABLE test_questions 
    ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;

    -- Mavjud yozuvlar uchun xavfsizlikni ta'minlash (DEFAULT ishlamagan taqdirda)
    UPDATE test_questions SET question_type = 'multiple_choice' WHERE question_type IS NULL;
    UPDATE test_questions SET options = '[]'::jsonb WHERE options IS NULL;
    UPDATE test_questions SET corre ct_answer = '' WHERE correct_answer IS NULL;
    UPDATE test_questions SET points = 1 WHERE points IS NULL;
    UPDATE test_questions SET difficulty = 'medium' WHERE difficulty IS NULL;
    UPDATE test_questions SET order_index = 0 WHERE order_index IS NULL;
    UPDATE test_questions SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL;

    -- Tezroq ishlashi uchun indekslar
    CREATE INDEX IF NOT EXISTS idx_test_questions_test_id ON test_questions(test_id);
    CREATE INDEX IF NOT EXISTS idx_test_questions_order ON test_questions(test_id, order_index);