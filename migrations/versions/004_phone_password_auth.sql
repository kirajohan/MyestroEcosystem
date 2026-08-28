-- Migration: 004_phone_password_auth.sql
-- Description: Telefon + password auth uchun users jadvalini tayyorlash

BEGIN;

-- 1. email ni nullable qilamiz (Telegram userlarda email bo'lmaydi)
ALTER TABLE users ALTER COLUMN email DROP NOT NULL;

-- 2. phone ni UNIQUE qilamiz (login uchun ishlatiladi)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'users_phone_key'
    ) THEN
        ALTER TABLE users ADD CONSTRAINT users_phone_key UNIQUE (phone);
    END IF;
END $$;

COMMIT;