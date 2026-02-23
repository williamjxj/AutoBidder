-- Migration 003: BiddingHub Merge
-- Created: 2026-01-12
-- Description: Add tables from BiddingHub (keywords, knowledge base, credentials, analytics)

---
--- TABLE: keywords
---
CREATE TABLE keywords (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
  
  -- Keyword Data
  keyword VARCHAR(255) NOT NULL,
  description TEXT,
  
  -- Configuration
  is_active BOOLEAN DEFAULT true,
  match_type VARCHAR(20) DEFAULT 'partial' CHECK (match_type IN ('exact', 'partial', 'fuzzy')),
  
  -- Statistics
  jobs_matched INT DEFAULT 0,
  last_match_at TIMESTAMP WITH TIME ZONE,
  
  -- Metadata
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for keywords
CREATE INDEX idx_keywords_user_id ON keywords(user_id);
CREATE INDEX idx_keywords_is_active ON keywords(is_active);
CREATE INDEX idx_keywords_keyword_lower ON keywords(LOWER(keyword));

-- Unique constraint: user can't have duplicate keywords
CREATE UNIQUE INDEX idx_keywords_user_keyword ON keywords(user_id, LOWER(keyword));

---
--- TABLE: knowledge_base_documents
---
CREATE TABLE knowledge_base_documents (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
  
  -- File Information
  filename VARCHAR(500) NOT NULL,
  file_type VARCHAR(10) NOT NULL CHECK (file_type IN ('pdf', 'docx', 'txt')),
  file_size_bytes BIGINT NOT NULL,
  file_url TEXT,
  
  -- Classification
  collection VARCHAR(50) NOT NULL CHECK (collection IN ('case_studies', 'team_profiles', 'portfolio', 'other')),
  
  -- Processing Status
  processing_status VARCHAR(20) DEFAULT 'pending' CHECK (processing_status IN ('pending', 'processing', 'completed', 'failed')),
  processing_error TEXT,
  
  -- Embedding Metadata
  chunk_count INT DEFAULT 0,
  token_count INT DEFAULT 0,
  embedding_model VARCHAR(50),
  chroma_collection_name VARCHAR(255),
  
  -- Usage Statistics
  retrieval_count INT DEFAULT 0,
  last_retrieved_at TIMESTAMP WITH TIME ZONE,
  
  -- Metadata
  uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  processed_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for knowledge_base_documents
CREATE INDEX idx_kb_docs_user_id ON knowledge_base_documents(user_id);
CREATE INDEX idx_kb_docs_collection ON knowledge_base_documents(collection);
CREATE INDEX idx_kb_docs_status ON knowledge_base_documents(processing_status);
CREATE INDEX idx_kb_docs_uploaded_at ON knowledge_base_documents(uploaded_at DESC);

---
--- TABLE: platform_credentials
---
CREATE TABLE platform_credentials (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
  
  -- Platform Information
  platform VARCHAR(50) NOT NULL CHECK (platform IN ('upwork', 'freelancer', 'custom')),
  
  -- Credentials (Encrypted - implement encryption in application layer)
  api_key TEXT,
  api_secret TEXT,
  access_token TEXT,
  refresh_token TEXT,
  expires_at TIMESTAMP WITH TIME ZONE,
  
  -- Status
  is_active BOOLEAN DEFAULT true,
  last_verified_at TIMESTAMP WITH TIME ZONE,
  verification_error TEXT,
  
  -- Metadata
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for platform_credentials
CREATE INDEX idx_platform_credentials_user_id ON platform_credentials(user_id);
CREATE INDEX idx_platform_credentials_platform ON platform_credentials(platform, is_active);

-- Unique constraint: One credential set per user per platform
CREATE UNIQUE INDEX idx_platform_credentials_user_platform ON platform_credentials(user_id, platform);

---
--- TABLE: scraping_jobs
---
CREATE TABLE scraping_jobs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  
  -- Job Configuration
  platform VARCHAR(50) NOT NULL,
  search_terms TEXT[] DEFAULT ARRAY[]::TEXT[],
  max_results INT DEFAULT 20,
  
  -- Execution Status
  status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed')),
  started_at TIMESTAMP WITH TIME ZONE,
  completed_at TIMESTAMP WITH TIME ZONE,
  
  -- Results
  jobs_found INT DEFAULT 0,
  jobs_new INT DEFAULT 0,
  jobs_duplicated INT DEFAULT 0,
  error_message TEXT,
  
  -- Metadata
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for scraping_jobs
CREATE INDEX idx_scraping_jobs_user_id ON scraping_jobs(user_id);
CREATE INDEX idx_scraping_jobs_status ON scraping_jobs(status);
CREATE INDEX idx_scraping_jobs_created_at ON scraping_jobs(created_at DESC);

---
--- TABLE: analytics_events
---
CREATE TABLE analytics_events (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  
  -- Event Data
  event_type VARCHAR(100) NOT NULL,
  event_data JSONB DEFAULT '{}'::jsonb,
  
  -- Context
  session_id VARCHAR(255),
  ip_address INET,
  user_agent TEXT,
  
  -- Metadata
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for analytics_events
CREATE INDEX idx_analytics_events_user_id ON analytics_events(user_id);
CREATE INDEX idx_analytics_events_type ON analytics_events(event_type);
CREATE INDEX idx_analytics_events_created_at ON analytics_events(created_at DESC);

---
--- Database Functions: Auto-update timestamps
---
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers to all tables with updated_at
CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bids_updated_at BEFORE UPDATE ON bids
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_strategies_updated_at BEFORE UPDATE ON bidding_strategies
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_keywords_updated_at BEFORE UPDATE ON keywords
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_kb_docs_updated_at BEFORE UPDATE ON knowledge_base_documents
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_credentials_updated_at BEFORE UPDATE ON platform_credentials
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

---
--- Database Functions: Usage quota reset
---
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

---
--- Database Functions: Increment strategy use count
---
CREATE OR REPLACE FUNCTION increment_strategy_use_count()
RETURNS TRIGGER AS $$
BEGIN
  UPDATE bidding_strategies
  SET use_count = use_count + 1
  WHERE id = NEW.strategy_id;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER increment_strategy_use AFTER INSERT ON bids
  FOR EACH ROW WHEN (NEW.strategy_id IS NOT NULL)
  EXECUTE FUNCTION increment_strategy_use_count();

-- Comments
COMMENT ON TABLE keywords IS 'User-defined search terms for job filtering';
COMMENT ON TABLE knowledge_base_documents IS 'Metadata for uploaded documents (embeddings in ChromaDB)';
COMMENT ON TABLE platform_credentials IS 'Encrypted API keys for Upwork/Freelancer';
COMMENT ON TABLE scraping_jobs IS 'Background scraping job status tracking';
COMMENT ON TABLE analytics_events IS 'User action tracking for analytics';
