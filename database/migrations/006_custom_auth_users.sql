-- Migration 006: Custom Authentication Users Table
-- Created: 2026-02-22
-- Description: Create custom users table for JWT authentication

-- Drop existing tables that reference auth.users
DROP TABLE IF EXISTS user_profiles CASCADE;

-- Create users table (replaces auth.users)
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  full_name VARCHAR(255),
  is_active BOOLEAN DEFAULT true,
  is_verified BOOLEAN DEFAULT false,
  email_verification_token VARCHAR(255),
  password_reset_token VARCHAR(255),
  password_reset_expires TIMESTAMP WITH TIME ZONE,
  last_login_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for users
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_is_active ON users(is_active);
CREATE INDEX idx_users_created_at ON users(created_at);

-- Recreate user_profiles table with reference to users table
CREATE TABLE user_profiles (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE NOT NULL,
  
  -- Subscription & Billing
  subscription_tier VARCHAR(20) DEFAULT 'free' CHECK (subscription_tier IN ('free', 'pro', 'agency')),
  subscription_status VARCHAR(20) DEFAULT 'active' CHECK (subscription_status IN ('active', 'cancelled', 'expired')),
  subscription_expires_at TIMESTAMP WITH TIME ZONE,
  
  -- Usage Tracking
  usage_quota JSONB DEFAULT '{"proposals_generated": 0, "proposals_limit": 10, "period_start": null}'::jsonb,
  
  -- User Preferences
  preferences JSONB DEFAULT '{
    "default_strategy_id": null,
    "notification_email": true,
    "notification_browser": true,
    "theme": "system",
    "language": "en"
  }'::jsonb,
  
  -- Metadata
  onboarding_completed BOOLEAN DEFAULT false,
  last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for user_profiles
CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX idx_user_profiles_subscription ON user_profiles(subscription_tier, subscription_status);
CREATE INDEX idx_user_profiles_last_activity ON user_profiles(last_activity_at);

-- Drop and recreate projects table with reference to users
DROP TABLE IF EXISTS projects CASCADE;

CREATE TABLE projects (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
  
  -- Job Details
  title VARCHAR(500) NOT NULL,
  description TEXT NOT NULL,
  budget DECIMAL(12, 2),
  budget_type VARCHAR(20) CHECK (budget_type IN ('fixed', 'hourly', 'not_specified')),
  technologies TEXT[] DEFAULT ARRAY[]::TEXT[],
  
  -- Source Information
  source_platform VARCHAR(50) NOT NULL CHECK (source_platform IN ('upwork', 'freelancer', 'manual', 'other')),
  source_url TEXT,
  external_id VARCHAR(255),
  
  -- Client Information
  client_rating VARCHAR(10),
  client_reviews_count INT,
  client_location VARCHAR(255),
  
  -- Discovery Metadata
  search_keyword VARCHAR(255),
  posted_date TIMESTAMP WITH TIME ZONE,
  deadline TIMESTAMP WITH TIME ZONE,
  
  -- Status Tracking
  status VARCHAR(20) DEFAULT 'new' CHECK (status IN ('new', 'reviewed', 'bidding', 'archived', 'won', 'lost')),
  
  -- Additional Metadata
  scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for projects
CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_projects_source_platform ON projects(source_platform);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_posted_date ON projects(posted_date DESC);
CREATE INDEX idx_projects_technologies ON projects USING GIN(technologies);
CREATE INDEX idx_projects_external_id ON projects(source_platform, external_id);

-- Full-text search index
CREATE INDEX idx_projects_fulltext ON projects USING GIN(to_tsvector('english', title || ' ' || description));

-- Unique constraint on external_id + source_platform
CREATE UNIQUE INDEX idx_projects_unique_external ON projects(source_platform, external_id) WHERE external_id IS NOT NULL;

-- Function to automatically create user_profile on user creation
CREATE OR REPLACE FUNCTION create_user_profile()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO user_profiles (user_id)
  VALUES (NEW.id);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to create profile when user signs up
CREATE TRIGGER on_user_created
  AFTER INSERT ON users
  FOR EACH ROW
  EXECUTE FUNCTION create_user_profile();

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at
CREATE TRIGGER update_users_updated_at
  BEFORE UPDATE ON users
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_profiles_updated_at
  BEFORE UPDATE ON user_profiles
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at
  BEFORE UPDATE ON projects
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();
