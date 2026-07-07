-- Phase 6: Structured Logging System
-- JSON-formatted logs with indexed queries for admin dashboard

CREATE TABLE logs (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    level VARCHAR(20) NOT NULL,  -- INFO, WARNING, ERROR, DEBUG, CRITICAL
    logger_name VARCHAR(255),
    message TEXT,
    module VARCHAR(255),
    function_name VARCHAR(255),
    line_number INTEGER,
    exception TEXT,
    user_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    extra_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for fast queries
CREATE INDEX idx_logs_timestamp ON logs(timestamp DESC);
CREATE INDEX idx_logs_level ON logs(level);
CREATE INDEX idx_logs_user_id ON logs(user_id);
CREATE INDEX idx_logs_logger_name ON logs(logger_name);
CREATE INDEX idx_logs_timestamp_level ON logs(timestamp DESC, level);
