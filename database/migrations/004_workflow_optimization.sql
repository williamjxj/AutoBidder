-- Migration 004: Workflow Optimization
-- Created: 2026-01-12
-- Description: Add tables for session state, draft management, and workflow analytics

-- Prerequisites: uuid-ossp extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Function for updated_at trigger (if not exists)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

---
--- TABLE: user_session_states
---
CREATE TABLE user_session_states (
  -- Primary Key
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL UNIQUE,
  
  -- Session Context
  active_feature VARCHAR(50), -- 'projects' | 'proposals' | 'keywords' | 'analytics' | 'knowledge-base' | 'settings'
  entity_id UUID, -- ID of currently viewed entity (project_id, proposal_id, etc.)
  
  -- Navigation State
  context_data JSONB DEFAULT '{}'::jsonb, -- { filters, selections, scrollPosition, tabs }
  navigation_history JSONB DEFAULT '[]'::jsonb, -- Last 10 navigation entries
  
  -- Metadata
  last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  -- Constraints
  CONSTRAINT active_feature_check CHECK (
    active_feature IN ('projects', 'proposals', 'keywords', 'analytics', 'knowledge-base', 'settings', 'strategies', 'dashboard')
  )
);

-- Indexes for user_session_states
CREATE UNIQUE INDEX idx_session_states_user_id ON user_session_states(user_id);
CREATE INDEX idx_session_states_last_activity ON user_session_states(last_activity_at);

-- Updated Timestamp Trigger for user_session_states
CREATE TRIGGER update_session_states_updated_at
  BEFORE UPDATE ON user_session_states
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

---
--- TABLE: draft_work
---
CREATE TABLE draft_work (
  -- Primary Key
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
  
  -- Entity Reference
  entity_type VARCHAR(50) NOT NULL, -- 'proposal' | 'project' | 'keyword' | 'knowledge_document'
  entity_id UUID, -- NULL for new entities not yet created
  
  -- Draft Data
  draft_data JSONB NOT NULL, -- Full entity data being edited
  draft_version INTEGER DEFAULT 1, -- Increment on each save (conflict detection)
  
  -- Auto-Save Metadata
  auto_save_count INTEGER DEFAULT 0, -- Number of auto-saves performed
  last_auto_save_at TIMESTAMP WITH TIME ZONE,
  
  -- Lifecycle
  is_recovered BOOLEAN DEFAULT false, -- User saw recovery prompt
  recovered_at TIMESTAMP WITH TIME ZONE,
  expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '24 hours'),
  
  -- Timestamps
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  -- Constraints
  CONSTRAINT entity_type_check CHECK (
    entity_type IN ('proposal', 'project', 'keyword', 'knowledge_document', 'strategy')
  ),
  CONSTRAINT draft_data_size_check CHECK (
    pg_column_size(draft_data) < 1048576  -- 1MB max
  )
);

-- Indexes for draft_work
CREATE UNIQUE INDEX idx_draft_work_user_entity ON draft_work(user_id, entity_type, entity_id) 
  WHERE entity_id IS NOT NULL;
CREATE INDEX idx_draft_work_expires_at ON draft_work(expires_at);
CREATE INDEX idx_draft_work_user_id ON draft_work(user_id);
CREATE INDEX idx_draft_work_is_recovered ON draft_work(is_recovered) 
  WHERE is_recovered = false;

-- Updated Timestamp Trigger for draft_work
CREATE TRIGGER update_draft_work_updated_at
  BEFORE UPDATE ON draft_work
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

---
--- TABLE: workflow_analytics
---
CREATE TABLE workflow_analytics (
  -- Primary Key
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  
  -- Event Data
  event_type VARCHAR(100) NOT NULL, -- 'navigation', 'auto_save', 'draft_recovery', 'offline_sync', etc.
  event_category VARCHAR(50), -- 'performance' | 'user_action' | 'error'
  
  -- Metrics
  duration_ms INTEGER, -- For timing events (navigation, save, etc.)
  success BOOLEAN, -- For operations that can fail
  error_message TEXT, -- If success = false
  
  -- Context
  metadata JSONB DEFAULT '{}'::jsonb, -- Event-specific data
  user_agent TEXT, -- Browser info
  
  -- Timestamp
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  -- Constraints
  CONSTRAINT event_category_check CHECK (
    event_category IN ('performance', 'user_action', 'error', 'recovery')
  )
);

-- Indexes for workflow_analytics
CREATE INDEX idx_workflow_analytics_user_id ON workflow_analytics(user_id);
CREATE INDEX idx_workflow_analytics_event_type ON workflow_analytics(event_type);
CREATE INDEX idx_workflow_analytics_created_at ON workflow_analytics(created_at);
CREATE INDEX idx_workflow_analytics_category ON workflow_analytics(event_category);

-- Comments for documentation
COMMENT ON TABLE user_session_states IS 'Stores user workflow state for context preservation';
COMMENT ON TABLE draft_work IS 'Auto-saved drafts with 24-hour retention';
COMMENT ON TABLE workflow_analytics IS 'Performance and usage analytics for workflow optimization';
