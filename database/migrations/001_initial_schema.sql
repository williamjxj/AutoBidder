-- Migration 001: Initial Schema (Base from BidMaster)
-- Created: 2026-01-12
-- Description: Core tables for auto-bidder platform

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable full-text search extension
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

---
--- TABLE: user_profiles
---
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

---
--- TABLE: projects
---
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

---
--- TABLE: bidding_strategies
---
CREATE TABLE bidding_strategies (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
  
  -- Strategy Definition
  name VARCHAR(255) NOT NULL,
  description TEXT,
  system_prompt TEXT NOT NULL,
  
  -- Style Configuration
  tone VARCHAR(50) DEFAULT 'professional' CHECK (tone IN ('professional', 'enthusiastic', 'technical', 'friendly', 'formal')),
  focus_areas JSONB DEFAULT '[]'::jsonb,
  
  -- Generation Parameters
  temperature DECIMAL(3, 2) DEFAULT 0.7 CHECK (temperature BETWEEN 0 AND 2),
  max_tokens INT DEFAULT 1500 CHECK (max_tokens BETWEEN 100 AND 4000),
  
  -- Usage
  is_default BOOLEAN DEFAULT false,
  use_count INT DEFAULT 0,
  
  -- Metadata
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for bidding_strategies
CREATE INDEX idx_strategies_user_id ON bidding_strategies(user_id);
CREATE INDEX idx_strategies_is_default ON bidding_strategies(user_id, is_default);

-- Unique constraint: Only one default strategy per user
CREATE UNIQUE INDEX idx_strategies_user_default ON bidding_strategies(user_id, is_default) WHERE is_default = true;

-- Unique constraint: Strategy name unique per user
CREATE UNIQUE INDEX idx_strategies_user_name ON bidding_strategies(user_id, LOWER(name));

---
--- TABLE: bids (proposals)
---
CREATE TABLE bids (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  project_id UUID REFERENCES projects(id) ON DELETE CASCADE NOT NULL,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
  strategy_id UUID REFERENCES bidding_strategies(id) ON DELETE SET NULL,
  
  -- Proposal Content
  proposal TEXT NOT NULL,
  cover_letter TEXT,
  bidding_statement TEXT,
  technical_approach TEXT,
  timeline TEXT,
  
  -- Evidence & Context
  relevant_projects JSONB DEFAULT '[]'::jsonb,
  
  -- Bid Details
  bid_amount DECIMAL(12, 2),
  estimated_hours INT,
  
  -- Generation Metadata
  ai_generated BOOLEAN DEFAULT true,
  generation_model VARCHAR(50),
  generation_tokens INT,
  
  -- Status Tracking
  status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'approved', 'submitted', 'won', 'lost', 'withdrawn')),
  submitted_at TIMESTAMP WITH TIME ZONE,
  response_received_at TIMESTAMP WITH TIME ZONE,
  
  -- Version Control
  version INT DEFAULT 1,
  parent_bid_id UUID REFERENCES bids(id),
  
  -- Metadata
  notes TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for bids
CREATE INDEX idx_bids_user_id ON bids(user_id);
CREATE INDEX idx_bids_project_id ON bids(project_id);
CREATE INDEX idx_bids_status ON bids(status);
CREATE INDEX idx_bids_strategy_id ON bids(strategy_id);
CREATE INDEX idx_bids_submitted_at ON bids(submitted_at DESC);
CREATE INDEX idx_bids_relevant_projects ON bids USING GIN(relevant_projects);

-- Comments
COMMENT ON TABLE user_profiles IS 'User profile information and preferences';
COMMENT ON TABLE projects IS 'Job postings from freelance platforms';
COMMENT ON TABLE bidding_strategies IS 'Reusable AI prompt templates for proposal generation';
COMMENT ON TABLE bids IS 'AI-generated and user-edited proposals';
