-- ============================================================
--  Virtual Queue System – Supabase SQL Schema
--  Run this in the Supabase SQL Editor (Dashboard → SQL Editor)
-- ============================================================

-- 1. Users table
CREATE TABLE IF NOT EXISTS users (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email      TEXT UNIQUE NOT NULL,
    password   TEXT NOT NULL,           -- store hashed passwords in production
    role       TEXT NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'admin')),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 2. Applications table
CREATE TABLE IF NOT EXISTS applications (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID REFERENCES users(id) ON DELETE CASCADE,
    email       TEXT NOT NULL,
    subject     TEXT NOT NULL,
    description TEXT,
    token       TEXT UNIQUE NOT NULL,
    status      TEXT NOT NULL DEFAULT 'Waiting' CHECK (status IN ('Waiting', 'Processing', 'Completed')),
    created_at  TIMESTAMPTZ DEFAULT now()
);

-- 3. Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_applications_user_id ON applications(user_id);
CREATE INDEX IF NOT EXISTS idx_applications_status  ON applications(status);
CREATE INDEX IF NOT EXISTS idx_applications_token   ON applications(token);

-- 4. Row-Level Security (RLS) – enable for production
-- ALTER TABLE users        ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE applications ENABLE ROW LEVEL SECURITY;

-- 5. Optional: seed an admin account
-- INSERT INTO users (email, password, role)
-- VALUES ('admin@example.com', 'changeme', 'admin')
-- ON CONFLICT (email) DO NOTHING;
