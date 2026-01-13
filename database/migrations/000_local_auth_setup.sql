-- Migration 000: Local Auth Setup
-- Created: 2026-01-12
-- Description: Create minimal auth schema for local PostgreSQL development
-- Note: This replicates basic Supabase auth structure for local testing

-- Create auth schema
CREATE SCHEMA IF NOT EXISTS auth;

-- Create basic users table for local development
CREATE TABLE IF NOT EXISTS auth.users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email VARCHAR(255) UNIQUE NOT NULL,
  encrypted_password VARCHAR(255),
  email_confirmed_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  last_sign_in_at TIMESTAMP WITH TIME ZONE,
  raw_app_meta_data JSONB,
  raw_user_meta_data JSONB,
  is_super_admin BOOLEAN DEFAULT false,
  role VARCHAR(255)
);

-- Create index on email
CREATE INDEX IF NOT EXISTS idx_auth_users_email ON auth.users(email);

-- Insert a test user for local development
INSERT INTO auth.users (id, email, email_confirmed_at, role)
VALUES (
  '00000000-0000-0000-0000-000000000001',
  'test@example.com',
  NOW(),
  'authenticated'
)
ON CONFLICT (email) DO NOTHING;

COMMENT ON SCHEMA auth IS 'Mock Supabase auth schema for local development';
COMMENT ON TABLE auth.users IS 'Simplified users table for local testing (replicates Supabase auth.users)';
