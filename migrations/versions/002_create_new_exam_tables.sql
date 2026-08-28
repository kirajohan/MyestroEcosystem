-- migrations/versions/002_create_new_exam_tables.sql

BEGIN;

-- =====================================================
-- 1. exams
-- =====================================================
CREATE TABLE IF NOT EXISTS exams (
    id BIGSERIAL PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    description TEXT,
    exam_type TEXT NOT NULL CHECK (
        exam_type IN (
            'full',
            'listening',
            'reading',
            'writing',
            'speaking'
        )
    ),
    cefr_level TEXT CHECK (
        cefr_level IN (
            'A1',
            'A2',
            'B1',
            'B2',
            'C1',
            'C2'
        )
    ),
    time_limit_sec INTEGER NOT NULL DEFAULT 0,
    is_published BOOLEAN NOT NULL DEFAULT FALSE,
    scoring_config JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- =====================================================
-- 2. exam_blocks
-- =====================================================
CREATE TABLE IF NOT EXISTS exam_blocks (
    id BIGSERIAL PRIMARY KEY,
    exam_id BIGINT NOT NULL REFERENCES exams(id) ON DELETE CASCADE,
    block_type TEXT NOT NULL CHECK (
        block_type IN (
            'listening',
            'reading',
            'writing',
            'speaking'
        )
    ),
    title TEXT NOT NULL,
    description TEXT,
    instructions TEXT,
    "order" INTEGER NOT NULL DEFAULT 0,
    time_limit_sec INTEGER NOT NULL DEFAULT 0,
    config JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_exam_blocks_exam_id
    ON exam_blocks(exam_id);

-- =====================================================
-- 3. exam_rubrics
-- =====================================================
CREATE TABLE IF NOT EXISTS exam_rubrics (
    id BIGSERIAL PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    skill_type TEXT NOT NULL CHECK (
        skill_type IN (
            'writing',
            'speaking'
        )
    ),
    system_prompt TEXT NOT NULL,
    user_prompt_template TEXT NOT NULL,
    scoring_schema JSONB NOT NULL DEFAULT '{}'::jsonb,
    cefr_mapping JSONB,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- =====================================================
-- 4. exam_items
-- =====================================================
CREATE TABLE IF NOT EXISTS exam_items (
    id BIGSERIAL PRIMARY KEY,
    block_id BIGINT NOT NULL REFERENCES exam_blocks(id) ON DELETE CASCADE,
    item_type TEXT NOT NULL CHECK (
        item_type IN (
            'listening_question',
            'reading_question',
            'writing_task',
            'speaking_task'
        )
    ),
    title TEXT,
    instruction TEXT,
    question_text TEXT,
    passage_text TEXT,
    audio_url TEXT,
    audio_duration_sec INTEGER,
    transcript_text TEXT,
    min_words INTEGER,
    max_words INTEGER,
    preparation_time_sec INTEGER,
    answer_time_sec INTEGER,
    max_score DOUBLE PRECISION NOT NULL DEFAULT 1.0,
    "order" INTEGER NOT NULL DEFAULT 0,
    config JSONB,
    answer_key JSONB,
    rubric_id BIGINT REFERENCES exam_rubrics(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_exam_items_block_id
    ON exam_items(block_id);

CREATE INDEX IF NOT EXISTS idx_exam_items_rubric_id
    ON exam_items(rubric_id);

-- =====================================================
-- 5. exam_options
-- =====================================================
CREATE TABLE IF NOT EXISTS exam_options (
    id BIGSERIAL PRIMARY KEY,
    item_id BIGINT NOT NULL REFERENCES exam_items(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL DEFAULT FALSE,
    "order" INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_exam_options_item_id
    ON exam_options(item_id);

-- =====================================================
-- 6. exam_attempts
-- =====================================================
CREATE TABLE IF NOT EXISTS exam_attempts (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    exam_id BIGINT NOT NULL REFERENCES exams(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'created' CHECK (
        status IN (
            'created',
            'in_progress',
            'submitted',
            'scoring',
            'completed',
            'needs_review',
            'failed'
        )
    ),
    started_at TIMESTAMPTZ,
    deadline TIMESTAMPTZ,
    submitted_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    total_score DOUBLE PRECISION,
    cefr_estimate TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_exam_attempts_user_id
    ON exam_attempts(user_id);

CREATE INDEX IF NOT EXISTS idx_exam_attempts_exam_id
    ON exam_attempts(exam_id);

CREATE INDEX IF NOT EXISTS idx_exam_attempts_status
    ON exam_attempts(status);

-- =====================================================
-- 7. exam_attempt_blocks
-- =====================================================
CREATE TABLE IF NOT EXISTS exam_attempt_blocks (
    id BIGSERIAL PRIMARY KEY,
    attempt_id BIGINT NOT NULL REFERENCES exam_attempts(id) ON DELETE CASCADE,
    block_id BIGINT NOT NULL REFERENCES exam_blocks(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (
        status IN (
            'pending',
            'in_progress',
            'completed',
            'skipped'
        )
    ),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    score DOUBLE PRECISION,
    metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_exam_attempt_blocks_attempt_id
    ON exam_attempt_blocks(attempt_id);

CREATE INDEX IF NOT EXISTS idx_exam_attempt_blocks_block_id
    ON exam_attempt_blocks(block_id);

-- =====================================================
-- 8. exam_answers
-- =====================================================
CREATE TABLE IF NOT EXISTS exam_answers (
    id BIGSERIAL PRIMARY KEY,
    attempt_id BIGINT NOT NULL REFERENCES exam_attempts(id) ON DELETE CASCADE,
    item_id BIGINT NOT NULL REFERENCES exam_items(id) ON DELETE CASCADE,
    selected_options JSONB,
    text_answer TEXT,
    audio_url TEXT,
    transcript_text TEXT,
    auto_score DOUBLE PRECISION,
    ai_score DOUBLE PRECISION,
    final_score DOUBLE PRECISION,
    ai_status TEXT CHECK (
        ai_status IN (
            'pending',
            'processing',
            'completed',
            'error',
            'needs_review'
        )
    ),
    feedback JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_exam_answers_attempt_id
    ON exam_answers(attempt_id);

CREATE INDEX IF NOT EXISTS idx_exam_answers_item_id
    ON exam_answers(item_id);

CREATE INDEX IF NOT EXISTS idx_exam_answers_ai_status
    ON exam_answers(ai_status);

-- =====================================================
-- 9. exam_ai_jobs
-- =====================================================
CREATE TABLE IF NOT EXISTS exam_ai_jobs (
    id BIGSERIAL PRIMARY KEY,
    attempt_id BIGINT NOT NULL REFERENCES exam_attempts(id) ON DELETE CASCADE,
    answer_id BIGINT REFERENCES exam_answers(id) ON DELETE SET NULL,
    job_type TEXT NOT NULL CHECK (
        job_type IN (
            'transcribe',
            'evaluate_writing',
            'evaluate_speaking'
        )
    ),
    status TEXT NOT NULL DEFAULT 'pending' CHECK (
        status IN (
            'pending',
            'processing',
            'completed',
            'error'
        )
    ),
    provider TEXT,
    request_payload JSONB,
    response_payload JSONB,
    error_message TEXT,
    attempts_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_exam_ai_jobs_attempt_id
    ON exam_ai_jobs(attempt_id);

CREATE INDEX IF NOT EXISTS idx_exam_ai_jobs_answer_id
    ON exam_ai_jobs(answer_id);

CREATE INDEX IF NOT EXISTS idx_exam_ai_jobs_status
    ON exam_ai_jobs(status);

-- =====================================================
-- 10. exam_media
-- =====================================================
CREATE TABLE IF NOT EXISTS exam_media (
    id BIGSERIAL PRIMARY KEY,
    owner_type TEXT NOT NULL,
    owner_id BIGINT NOT NULL,
    file_type TEXT NOT NULL CHECK (
        file_type IN (
            'audio',
            'image',
            'document'
        )
    ),
    file_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    mime_type TEXT NOT NULL,
    size_bytes BIGINT NOT NULL DEFAULT 0,
    duration_sec INTEGER,
    transcript_text TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_exam_media_owner
    ON exam_media(owner_type, owner_id);

COMMIT;