-- ============================================================
-- Exam System Tables (CEFR Tests)
-- 5 tables: exams, exam_sections, exam_questions, exam_attempts, exam_answers
-- Model: telegram_bot/backend/app/models/exam.py
-- ============================================================

-- -----------------------------------------------------------
-- 1. exams
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS exams (
    id                BIGSERIAL PRIMARY KEY,
    title             VARCHAR(255) NOT NULL,
    description       TEXT,
    cefr_level        VARCHAR(10) NOT NULL,
    status            VARCHAR(20) DEFAULT 'draft',
    total_duration    INTEGER DEFAULT 0,
    reading_duration  INTEGER DEFAULT 0,
    listening_duration INTEGER DEFAULT 0,
    speaking_duration INTEGER DEFAULT 0,
    writing_duration  INTEGER DEFAULT 0,
    ownership_type    VARCHAR(20) DEFAULT 'owned',
    partner_name      VARCHAR(255),
    pdf_url           TEXT,
    mp3_url           TEXT,
    passing_score     DECIMAL(5, 2),
    max_score         DECIMAL(5, 2),
    version           INTEGER DEFAULT 1,
    is_sample         BOOLEAN DEFAULT FALSE,
    is_active         BOOLEAN DEFAULT TRUE NOT NULL,
    attempt_limit     INTEGER DEFAULT 1,
    created_by        BIGINT REFERENCES users(id) ON DELETE SET NULL,
    created_at        TIMESTAMPTZ DEFAULT NOW(),
    updated_at        TIMESTAMPTZ DEFAULT NOW(),
    deleted_at        TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_exams_cefr_level ON exams(cefr_level);
CREATE INDEX IF NOT EXISTS idx_exams_status ON exams(status);
CREATE INDEX IF NOT EXISTS idx_exams_is_active ON exams(is_active);
CREATE INDEX IF NOT EXISTS idx_exams_deleted_at ON exams(deleted_at);
CREATE INDEX IF NOT EXISTS idx_exams_created_at ON exams(created_at DESC);

-- -----------------------------------------------------------
-- 2. exam_sections
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS exam_sections (
    id               BIGSERIAL PRIMARY KEY,
    exam_id          BIGINT NOT NULL REFERENCES exams(id) ON DELETE CASCADE,
    section_type     VARCHAR(20) NOT NULL,
    title            VARCHAR(255) NOT NULL,
    description      TEXT,
    duration_minutes INTEGER DEFAULT 0,
    order_index      INTEGER DEFAULT 0,
    instructions     TEXT,
    total_questions  INTEGER DEFAULT 0,
    max_score        DECIMAL(5, 2),
    passing_score    DECIMAL(5, 2),
    created_at       TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_exam_sections_exam_id ON exam_sections(exam_id);
CREATE INDEX IF NOT EXISTS idx_exam_sections_order ON exam_sections(order_index);

-- -----------------------------------------------------------
-- 3. exam_questions
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS exam_questions (
    id              BIGSERIAL PRIMARY KEY,
    section_id      BIGINT NOT NULL REFERENCES exam_sections(id) ON DELETE CASCADE,
    question_number INTEGER DEFAULT 0,
    question_type   VARCHAR(50) DEFAULT 'multiple_choice',
    question_text   TEXT NOT NULL,
    options         JSONB,
    correct_answer  TEXT NOT NULL,
    explanation     TEXT,
    points          DECIMAL(5, 2) DEFAULT 1.00,
    difficulty      VARCHAR(20) DEFAULT 'medium',
    audio_url       TEXT,
    image_url       TEXT,
    order_index     INTEGER DEFAULT 0,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_exam_questions_section_id ON exam_questions(section_id);
CREATE INDEX IF NOT EXISTS idx_exam_questions_order ON exam_questions(order_index);

-- -----------------------------------------------------------
-- 4. exam_attempts
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS exam_attempts (
    id                BIGSERIAL PRIMARY KEY,
    exam_id           BIGINT NOT NULL REFERENCES exams(id) ON DELETE CASCADE,
    user_id           BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    attempt_number    INTEGER DEFAULT 1,
    status            VARCHAR(20) DEFAULT 'in_progress',
    started_at        TIMESTAMPTZ DEFAULT NOW(),
    submitted_at      TIMESTAMPTZ,
    reading_score     DECIMAL(5, 2),
    listening_score   DECIMAL(5, 2),
    speaking_score    DECIMAL(5, 2),
    writing_score     DECIMAL(5, 2),
    speaking_feedback TEXT,
    writing_feedback  TEXT,
    total_score       DECIMAL(5, 2),
    cefr_result       VARCHAR(10),
    passed            BOOLEAN,
    confidence_score  DECIMAL(5, 2),
    created_at        TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_exam_attempts_exam_user_attempt UNIQUE (exam_id, user_id, attempt_number)
);

CREATE INDEX IF NOT EXISTS idx_exam_attempts_exam_id ON exam_attempts(exam_id);
CREATE INDEX IF NOT EXISTS idx_exam_attempts_user_id ON exam_attempts(user_id);
CREATE INDEX IF NOT EXISTS idx_exam_attempts_status ON exam_attempts(status);

-- -----------------------------------------------------------
-- 5. exam_answers
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS exam_answers (
    id           BIGSERIAL PRIMARY KEY,
    attempt_id   BIGINT NOT NULL REFERENCES exam_attempts(id) ON DELETE CASCADE,
    question_id  BIGINT NOT NULL REFERENCES exam_questions(id) ON DELETE CASCADE,
    user_answer  TEXT,
    is_correct   BOOLEAN,
    score        DECIMAL(5, 2),
    ai_feedback  TEXT,
    answered_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_exam_answers_attempt_id ON exam_answers(attempt_id);
CREATE INDEX IF NOT EXISTS idx_exam_answers_question_id ON exam_answers(question_id);