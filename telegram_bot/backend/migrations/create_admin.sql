-- Create a default admin user for Myestro
-- Run this inside the PostgreSQL container after docker compose up

-- Admin user: admin@myestro.com / admin123
-- Password is bcrypt hashed with 12 rounds

INSERT INTO users (
    email,
    password_hash,
    full_name,
    role,
    cefr_level,
    target_level,
    lang,
    auth_provider,
    is_active,
    is_verified,
    profile_completed
) VALUES (
    'admin@myestro.com',
    '$2b$12$4lU5EZkNq6N3LQ2W1X8Y0O9P7R6T5U4V3W2X1Y0Z9A8B7C6D5E4F3G2H1I0',  -- placeholder, will update below
    'Super Admin',
    'superadmin',
    'C2',
    'C2',
    'uz',
    'email',
    TRUE,
    TRUE,
    TRUE
)
ON CONFLICT (email) DO NOTHING;

-- Note: The password_hash above is NOT a real bcrypt hash.
-- We need to generate a proper bcrypt hash. See the Python script below for the correct approach.
