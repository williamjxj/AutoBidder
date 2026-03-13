-- Migration 001: Initial Schema (Consolidated baseline)
-- Created: 2026-01-12
-- Description: Current canonical schema for the auto-bidder platform.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ============================================================
-- USERS
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
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

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);

-- ============================================================
-- USER PROFILES
-- ============================================================
CREATE TABLE IF NOT EXISTS user_profiles (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE NOT NULL,

  subscription_tier VARCHAR(20) DEFAULT 'free' CHECK (subscription_tier IN ('free', 'pro', 'agency')),
  subscription_status VARCHAR(20) DEFAULT 'active' CHECK (subscription_status IN ('active', 'cancelled', 'expired')),
  subscription_expires_at TIMESTAMP WITH TIME ZONE,

  usage_quota JSONB DEFAULT '{"proposals_generated": 0, "proposals_limit": 10, "period_start": null}'::jsonb,
  preferences JSONB DEFAULT '{
    "default_strategy_id": null,
    "notification_email": true,
    "notification_browser": true,
    "theme": "system",
    "language": "en"
  }'::jsonb,

  auto_discovery_enabled BOOLEAN DEFAULT false,
  discovery_interval_minutes INTEGER DEFAULT 15,
  notifications_enabled BOOLEAN DEFAULT true,
  auto_generate_enabled BOOLEAN DEFAULT false,
  autonomy_level VARCHAR(20) DEFAULT 'assisted',

  onboarding_completed BOOLEAN DEFAULT false,
  last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

  CONSTRAINT chk_autonomy_level CHECK (
    autonomy_level IN ('assisted', 'discovery_only', 'semi_autonomous', 'full_auto_generate')
  )
);

CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_profiles_subscription ON user_profiles(subscription_tier, subscription_status);
CREATE INDEX IF NOT EXISTS idx_user_profiles_last_activity ON user_profiles(last_activity_at);
CREATE INDEX IF NOT EXISTS idx_user_profiles_auto_discovery
  ON user_profiles(auto_discovery_enabled)
  WHERE auto_discovery_enabled = true;

-- ============================================================
-- ENUMS
-- ============================================================
DO $$ BEGIN
    CREATE TYPE job_platform AS ENUM (
        'upwork', 'freelancer', 'linkedin', 'toptal', 'guru',
        'remoteok', 'remotive', 'huggingface_dataset', 'other', 'manual'
    );
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE job_category AS ENUM (
        'ai_ml', 'web_development', 'fullstack_engineering',
        'devops_mlops', 'cloud_infrastructure',
        'software_outsourcing', 'ui_design', 'other'
    );
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE job_status AS ENUM (
        'new', 'matched', 'archived', 'expired'
    );
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

-- ============================================================
-- PROJECTS (ETL-backed opportunities)
-- ============================================================
CREATE TABLE IF NOT EXISTS projects (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

  platform job_platform NOT NULL,
  external_id TEXT NOT NULL,
  external_url TEXT,
  fingerprint_hash TEXT NOT NULL UNIQUE,

  category job_category NOT NULL,
  subcategory TEXT,

  title TEXT NOT NULL,
  description TEXT NOT NULL,
  skills_required TEXT[] DEFAULT ARRAY[]::TEXT[],

  budget_min NUMERIC(12,2),
  budget_max NUMERIC(12,2),
  budget_currency CHAR(3) DEFAULT 'USD',

  employer_name TEXT,
  status job_status DEFAULT 'new',
  etl_source TEXT,
  raw_payload JSONB,
  test_email TEXT,

  posted_at TIMESTAMPTZ,
  scraped_at TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_projects_platform ON projects(platform);
CREATE INDEX IF NOT EXISTS idx_projects_category ON projects(category);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_projects_posted_at ON projects(posted_at DESC);
CREATE INDEX IF NOT EXISTS idx_projects_fingerprint ON projects(fingerprint_hash);
CREATE INDEX IF NOT EXISTS idx_projects_skills ON projects USING GIN(skills_required);
CREATE INDEX IF NOT EXISTS idx_projects_fulltext ON projects USING GIN(to_tsvector('english', title || ' ' || description));

-- ============================================================
-- BIDDING STRATEGIES
-- ============================================================
CREATE TABLE IF NOT EXISTS bidding_strategies (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  system_prompt TEXT NOT NULL,
  tone VARCHAR(50) DEFAULT 'professional' CHECK (tone IN ('professional', 'enthusiastic', 'technical', 'friendly', 'formal')),
  focus_areas JSONB DEFAULT '[]'::jsonb,
  temperature DECIMAL(3, 2) DEFAULT 0.7 CHECK (temperature BETWEEN 0 AND 2),
  max_tokens INT DEFAULT 1500 CHECK (max_tokens BETWEEN 100 AND 4000),
  is_default BOOLEAN DEFAULT false,
  use_count INT DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_strategies_user_id ON bidding_strategies(user_id);
CREATE INDEX IF NOT EXISTS idx_strategies_is_default ON bidding_strategies(user_id, is_default);
CREATE UNIQUE INDEX IF NOT EXISTS idx_strategies_user_default ON bidding_strategies(user_id, is_default) WHERE is_default = true;
CREATE UNIQUE INDEX IF NOT EXISTS idx_strategies_user_name ON bidding_strategies(user_id, LOWER(name));

-- ============================================================
-- PROPOSALS
-- ============================================================
CREATE TABLE IF NOT EXISTS proposals (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
  project_id UUID REFERENCES projects(id) ON DELETE SET NULL,

  title VARCHAR(500) NOT NULL,
  description TEXT NOT NULL,
  budget DECIMAL(12, 2),
  timeline VARCHAR(200),
  skills TEXT[],

  job_url TEXT,
  job_platform VARCHAR(100),
  client_name VARCHAR(255),
  recipient_email VARCHAR(255),
  job_identifier VARCHAR(255),

  strategy_id UUID REFERENCES bidding_strategies(id) ON DELETE SET NULL,
  generated_with_ai BOOLEAN DEFAULT false,
  ai_model_used VARCHAR(100),

  status VARCHAR(50) DEFAULT 'draft' CHECK (status IN ('draft', 'submitted', 'accepted', 'rejected', 'withdrawn')),
  source VARCHAR(20) DEFAULT 'manual' CHECK (source IN ('manual', 'auto_generated')),
  auto_generated_at TIMESTAMPTZ,
  submitted_at TIMESTAMP WITH TIME ZONE,
  response_at TIMESTAMP WITH TIME ZONE,

  view_count INT DEFAULT 0,
  revision_count INT DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_proposals_user_id ON proposals(user_id);
CREATE INDEX IF NOT EXISTS idx_proposals_status ON proposals(status);
CREATE INDEX IF NOT EXISTS idx_proposals_created_at ON proposals(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_proposals_user_status ON proposals(user_id, status);
CREATE INDEX IF NOT EXISTS idx_proposals_project_id ON proposals(project_id);
CREATE INDEX IF NOT EXISTS idx_proposals_job_identifier ON proposals(job_identifier) WHERE job_identifier IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_proposals_user_job_identifier ON proposals(user_id, job_identifier) WHERE job_identifier IS NOT NULL;

-- ============================================================
-- ETL RUNS + USER PROJECT STATUS + AUTONOMOUS RUNS
-- ============================================================
CREATE TABLE IF NOT EXISTS etl_runs (
  id SERIAL PRIMARY KEY,
  source TEXT NOT NULL,
  started_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ,
  status TEXT,
  jobs_extracted INT DEFAULT 0,
  jobs_filtered INT DEFAULT 0,
  jobs_inserted INT DEFAULT 0,
  jobs_updated INT DEFAULT 0,
  error_message TEXT,
  metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_etl_runs_source ON etl_runs(source);
CREATE INDEX IF NOT EXISTS idx_etl_runs_started_at ON etl_runs(started_at DESC);

CREATE TABLE IF NOT EXISTS user_project_status (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  status VARCHAR(20) NOT NULL CHECK (status IN ('reviewed', 'applied', 'won', 'lost', 'archived')),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (user_id, project_id)
);

CREATE INDEX IF NOT EXISTS idx_user_project_status_user_id ON user_project_status(user_id);
CREATE INDEX IF NOT EXISTS idx_user_project_status_project_id ON user_project_status(project_id);
CREATE INDEX IF NOT EXISTS idx_user_project_status_status ON user_project_status(status);

CREATE TABLE IF NOT EXISTS autonomous_runs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  started_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ,
  status VARCHAR(20) NOT NULL DEFAULT 'running',
  jobs_discovered INTEGER DEFAULT 0,
  proposals_generated INTEGER DEFAULT 0,
  notifications_sent INTEGER DEFAULT 0,
  errors JSONB,
  metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_autonomous_runs_user_id ON autonomous_runs(user_id);
CREATE INDEX IF NOT EXISTS idx_autonomous_runs_started_at ON autonomous_runs(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_autonomous_runs_status ON autonomous_runs(status);

-- ============================================================
-- KEYWORDS + KNOWLEDGE BASE + CREDENTIALS + ANALYTICS
-- ============================================================
CREATE TABLE IF NOT EXISTS keywords (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
  keyword VARCHAR(255) NOT NULL,
  description TEXT,
  is_active BOOLEAN DEFAULT true,
  match_type VARCHAR(20) DEFAULT 'partial' CHECK (match_type IN ('exact', 'partial', 'fuzzy')),
  jobs_matched INT DEFAULT 0,
  last_match_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_keywords_user_id ON keywords(user_id);
CREATE INDEX IF NOT EXISTS idx_keywords_is_active ON keywords(is_active);
CREATE INDEX IF NOT EXISTS idx_keywords_keyword_lower ON keywords(LOWER(keyword));
CREATE UNIQUE INDEX IF NOT EXISTS idx_keywords_user_keyword ON keywords(user_id, LOWER(keyword));

CREATE TABLE IF NOT EXISTS knowledge_base_documents (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
  filename VARCHAR(500) NOT NULL,
  file_type VARCHAR(10) NOT NULL CHECK (file_type IN ('pdf', 'docx', 'txt')),
  file_size_bytes BIGINT NOT NULL,
  file_url TEXT,
  collection VARCHAR(50) NOT NULL CHECK (collection IN ('case_studies', 'team_profiles', 'portfolio', 'other')),
  processing_status VARCHAR(20) DEFAULT 'pending' CHECK (processing_status IN ('pending', 'processing', 'completed', 'failed')),
  processing_error TEXT,
  chunk_count INT DEFAULT 0,
  token_count INT DEFAULT 0,
  embedding_model VARCHAR(50),
  chroma_collection_name VARCHAR(255),
  retrieval_count INT DEFAULT 0,
  last_retrieved_at TIMESTAMP WITH TIME ZONE,
  title VARCHAR(200),
  reference_url TEXT,
  email VARCHAR(255),
  phone VARCHAR(50),
  contact_url TEXT,
  uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  processed_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_kb_docs_user_id ON knowledge_base_documents(user_id);
CREATE INDEX IF NOT EXISTS idx_kb_docs_collection ON knowledge_base_documents(collection);
CREATE INDEX IF NOT EXISTS idx_kb_docs_status ON knowledge_base_documents(processing_status);
CREATE INDEX IF NOT EXISTS idx_kb_docs_uploaded_at ON knowledge_base_documents(uploaded_at DESC);
CREATE INDEX IF NOT EXISTS idx_kb_docs_title ON knowledge_base_documents(title);
CREATE INDEX IF NOT EXISTS idx_kb_docs_email ON knowledge_base_documents(email) WHERE email IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_kb_docs_phone ON knowledge_base_documents(phone) WHERE phone IS NOT NULL;

CREATE TABLE IF NOT EXISTS platform_credentials (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
  platform VARCHAR(50) NOT NULL CHECK (platform IN ('upwork', 'freelancer', 'custom')),
  api_key TEXT,
  api_secret TEXT,
  access_token TEXT,
  refresh_token TEXT,
  expires_at TIMESTAMP WITH TIME ZONE,
  is_active BOOLEAN DEFAULT true,
  last_verified_at TIMESTAMP WITH TIME ZONE,
  verification_error TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_platform_credentials_user_id ON platform_credentials(user_id);
CREATE INDEX IF NOT EXISTS idx_platform_credentials_platform ON platform_credentials(platform, is_active);
CREATE UNIQUE INDEX IF NOT EXISTS idx_platform_credentials_user_platform ON platform_credentials(user_id, platform);

CREATE TABLE IF NOT EXISTS scraping_jobs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  platform VARCHAR(50) NOT NULL,
  search_terms TEXT[] DEFAULT ARRAY[]::TEXT[],
  max_results INT DEFAULT 20,
  status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed')),
  started_at TIMESTAMP WITH TIME ZONE,
  completed_at TIMESTAMP WITH TIME ZONE,
  jobs_found INT DEFAULT 0,
  jobs_new INT DEFAULT 0,
  jobs_duplicated INT DEFAULT 0,
  error_message TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_scraping_jobs_user_id ON scraping_jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_scraping_jobs_status ON scraping_jobs(status);
CREATE INDEX IF NOT EXISTS idx_scraping_jobs_created_at ON scraping_jobs(created_at DESC);

CREATE TABLE IF NOT EXISTS analytics_events (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  event_type VARCHAR(100) NOT NULL,
  event_data JSONB DEFAULT '{}'::jsonb,
  session_id VARCHAR(255),
  ip_address INET,
  user_agent TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_analytics_events_user_id ON analytics_events(user_id);
CREATE INDEX IF NOT EXISTS idx_analytics_events_type ON analytics_events(event_type);
CREATE INDEX IF NOT EXISTS idx_analytics_events_created_at ON analytics_events(created_at DESC);

-- ============================================================
-- WORKFLOW STATE TABLES
-- ============================================================
CREATE TABLE IF NOT EXISTS user_session_states (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL UNIQUE,
  active_feature VARCHAR(50),
  active_entity_type VARCHAR(50),
  entity_id UUID,
  context_data JSONB DEFAULT '{}'::jsonb,
  navigation_history JSONB DEFAULT '[]'::jsonb,
  current_path VARCHAR(500) NOT NULL DEFAULT '/',
  scroll_position JSONB DEFAULT '{}'::jsonb,
  filters JSONB DEFAULT '{}'::jsonb,
  ui_state JSONB DEFAULT '{}'::jsonb,
  last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  CONSTRAINT active_feature_check CHECK (
    active_feature IN ('projects', 'proposals', 'keywords', 'analytics', 'knowledge-base', 'settings', 'strategies', 'dashboard')
  )
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_session_states_user_id ON user_session_states(user_id);
CREATE INDEX IF NOT EXISTS idx_session_states_last_activity ON user_session_states(last_activity_at);
CREATE INDEX IF NOT EXISTS idx_session_states_current_path ON user_session_states(current_path);
CREATE INDEX IF NOT EXISTS idx_session_states_active_entity_type ON user_session_states(active_entity_type);

CREATE TABLE IF NOT EXISTS draft_work (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
  entity_type VARCHAR(50) NOT NULL,
  entity_id UUID,
  draft_data JSONB NOT NULL,
  draft_version INTEGER DEFAULT 1,
  auto_save_count INTEGER DEFAULT 0,
  last_auto_save_at TIMESTAMP WITH TIME ZONE,
  is_recovered BOOLEAN DEFAULT false,
  recovered_at TIMESTAMP WITH TIME ZONE,
  expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '24 hours'),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  CONSTRAINT entity_type_check CHECK (
    entity_type IN ('proposal', 'project', 'keyword', 'knowledge_document', 'strategy')
  ),
  CONSTRAINT draft_data_size_check CHECK (pg_column_size(draft_data) < 1048576)
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_draft_work_user_entity ON draft_work(user_id, entity_type, entity_id) WHERE entity_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_draft_work_expires_at ON draft_work(expires_at);
CREATE INDEX IF NOT EXISTS idx_draft_work_user_id ON draft_work(user_id);
CREATE INDEX IF NOT EXISTS idx_draft_work_is_recovered ON draft_work(is_recovered) WHERE is_recovered = false;

CREATE TABLE IF NOT EXISTS workflow_analytics (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  event_type VARCHAR(100) NOT NULL,
  event_category VARCHAR(50),
  duration_ms INTEGER,
  success BOOLEAN,
  error_message TEXT,
  metadata JSONB DEFAULT '{}'::jsonb,
  user_agent TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  CONSTRAINT event_category_check CHECK (event_category IN ('performance', 'user_action', 'error', 'recovery'))
);

CREATE INDEX IF NOT EXISTS idx_workflow_analytics_user_id ON workflow_analytics(user_id);
CREATE INDEX IF NOT EXISTS idx_workflow_analytics_event_type ON workflow_analytics(event_type);
CREATE INDEX IF NOT EXISTS idx_workflow_analytics_created_at ON workflow_analytics(created_at);
CREATE INDEX IF NOT EXISTS idx_workflow_analytics_category ON workflow_analytics(event_category);

-- ============================================================
-- FUNCTIONS + TRIGGERS
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION create_user_profile()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO user_profiles (user_id)
  VALUES (NEW.id)
  ON CONFLICT (user_id) DO NOTHING;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS on_user_created ON users;
CREATE TRIGGER on_user_created
  AFTER INSERT ON users
  FOR EACH ROW
  EXECUTE FUNCTION create_user_profile();

CREATE OR REPLACE FUNCTION reset_usage_quotas()
RETURNS void AS $$
BEGIN
  UPDATE user_profiles
  SET usage_quota = jsonb_set(
    usage_quota,
    '{proposals_generated}',
    '0',
    true
  )
  WHERE (usage_quota->>'period_start')::timestamp < NOW() - INTERVAL '30 days';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION increment_strategy_use_count()
RETURNS TRIGGER AS $$
BEGIN
  UPDATE bidding_strategies
  SET use_count = use_count + 1
  WHERE id = NEW.strategy_id;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_user_profiles_updated_at ON user_profiles;
CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_projects_updated_at ON projects;
CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_strategies_updated_at ON bidding_strategies;
CREATE TRIGGER update_strategies_updated_at BEFORE UPDATE ON bidding_strategies
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_proposals_updated_at ON proposals;
CREATE TRIGGER update_proposals_updated_at BEFORE UPDATE ON proposals
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_keywords_updated_at ON keywords;
CREATE TRIGGER update_keywords_updated_at BEFORE UPDATE ON keywords
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_kb_docs_updated_at ON knowledge_base_documents;
CREATE TRIGGER update_kb_docs_updated_at BEFORE UPDATE ON knowledge_base_documents
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_credentials_updated_at ON platform_credentials;
CREATE TRIGGER update_credentials_updated_at BEFORE UPDATE ON platform_credentials
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_session_states_updated_at ON user_session_states;
CREATE TRIGGER update_session_states_updated_at BEFORE UPDATE ON user_session_states
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_draft_work_updated_at ON draft_work;
CREATE TRIGGER update_draft_work_updated_at BEFORE UPDATE ON draft_work
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_user_project_status_updated_at ON user_project_status;
CREATE TRIGGER update_user_project_status_updated_at BEFORE UPDATE ON user_project_status
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS increment_strategy_use_proposals ON proposals;
CREATE TRIGGER increment_strategy_use_proposals
  AFTER INSERT ON proposals
  FOR EACH ROW
  WHEN (NEW.strategy_id IS NOT NULL)
  EXECUTE FUNCTION increment_strategy_use_count();
