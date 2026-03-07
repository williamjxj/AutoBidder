-- Migration 010: Autonomous Bidding Settings
-- Created: 2026-03-07
-- Description: Autonomy columns for user_profiles, user_job_qualifications, autonomous_runs, proposals extensions
-- Reference: specs/004-improve-autonomous/data-model.md

-- ============================================================
-- USER_PROFILES: Autonomy columns
-- ============================================================

ALTER TABLE user_profiles
  ADD COLUMN IF NOT EXISTS auto_discovery_enabled BOOLEAN DEFAULT false,
  ADD COLUMN IF NOT EXISTS discovery_interval_minutes INTEGER DEFAULT 15,
  ADD COLUMN IF NOT EXISTS qualification_threshold NUMERIC(3,2) DEFAULT 0.60,
  ADD COLUMN IF NOT EXISTS notification_threshold NUMERIC(3,2) DEFAULT 0.80,
  ADD COLUMN IF NOT EXISTS notifications_enabled BOOLEAN DEFAULT true,
  ADD COLUMN IF NOT EXISTS auto_generate_enabled BOOLEAN DEFAULT false,
  ADD COLUMN IF NOT EXISTS auto_generate_threshold NUMERIC(3,2) DEFAULT 0.85,
  ADD COLUMN IF NOT EXISTS autonomy_level VARCHAR(20) DEFAULT 'assisted';

-- Constraint for autonomy_level (add only if not exists)
DO $$ BEGIN
  ALTER TABLE user_profiles
    ADD CONSTRAINT chk_autonomy_level
    CHECK (autonomy_level IN ('assisted', 'discovery_only', 'semi_autonomous', 'full_auto_generate'));
EXCEPTION
  WHEN duplicate_object THEN NULL;
END $$;

-- Index for scheduler: users with auto-discovery enabled
CREATE INDEX IF NOT EXISTS idx_user_profiles_auto_discovery
  ON user_profiles(auto_discovery_enabled)
  WHERE auto_discovery_enabled = true;

COMMENT ON COLUMN user_profiles.auto_discovery_enabled IS 'Run discovery for this user on schedule';
COMMENT ON COLUMN user_profiles.discovery_interval_minutes IS 'Minutes between discovery runs';
COMMENT ON COLUMN user_profiles.qualification_threshold IS 'Min score (0-1) for job to appear as qualified';
COMMENT ON COLUMN user_profiles.notification_threshold IS 'Min score to trigger notification';
COMMENT ON COLUMN user_profiles.notifications_enabled IS 'Send email when high-quality jobs found';
COMMENT ON COLUMN user_profiles.auto_generate_enabled IS 'Auto-generate proposals for high-confidence jobs';
COMMENT ON COLUMN user_profiles.auto_generate_threshold IS 'Min score to auto-generate proposal';
COMMENT ON COLUMN user_profiles.autonomy_level IS 'assisted, discovery_only, semi_autonomous, full_auto_generate';

-- ============================================================
-- USER_JOB_QUALIFICATIONS: Per-user qualification scores
-- ============================================================

CREATE TABLE IF NOT EXISTS user_job_qualifications (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
  qualification_score NUMERIC(3,2) NOT NULL,
  qualification_reason TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, job_id)
);

CREATE INDEX IF NOT EXISTS idx_user_job_qualifications_user_id ON user_job_qualifications(user_id);
CREATE INDEX IF NOT EXISTS idx_user_job_qualifications_job_id ON user_job_qualifications(job_id);

COMMENT ON TABLE user_job_qualifications IS 'Per-user qualification scores for jobs';

-- ============================================================
-- AUTONOMOUS_RUNS: Audit trail for pipeline executions
-- ============================================================

CREATE TABLE IF NOT EXISTS autonomous_runs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  started_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ,
  status VARCHAR(20) NOT NULL DEFAULT 'running',
  jobs_discovered INTEGER DEFAULT 0,
  jobs_qualified INTEGER DEFAULT 0,
  proposals_generated INTEGER DEFAULT 0,
  notifications_sent INTEGER DEFAULT 0,
  errors JSONB,
  metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_autonomous_runs_user_id ON autonomous_runs(user_id);
CREATE INDEX IF NOT EXISTS idx_autonomous_runs_started_at ON autonomous_runs(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_autonomous_runs_status ON autonomous_runs(status);

COMMENT ON TABLE autonomous_runs IS 'Audit trail for autonomous pipeline executions';

-- ============================================================
-- PROPOSALS: Extensions for auto-generated and quality
-- ============================================================

ALTER TABLE proposals
  ADD COLUMN IF NOT EXISTS source VARCHAR(20) DEFAULT 'manual',
  ADD COLUMN IF NOT EXISTS auto_generated_at TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS quality_score INTEGER,
  ADD COLUMN IF NOT EXISTS quality_breakdown JSONB,
  ADD COLUMN IF NOT EXISTS quality_suggestions TEXT[];

-- Constraint for source
DO $$ BEGIN
  ALTER TABLE proposals
    ADD CONSTRAINT chk_proposals_source
    CHECK (source IN ('manual', 'auto_generated'));
EXCEPTION
  WHEN duplicate_object THEN NULL;
END $$;

COMMENT ON COLUMN proposals.source IS 'manual or auto_generated';
COMMENT ON COLUMN proposals.auto_generated_at IS 'When auto-generated (if source=auto_generated)';
COMMENT ON COLUMN proposals.quality_score IS '0-100 overall quality';
COMMENT ON COLUMN proposals.quality_breakdown IS 'Dimension scores (length, coverage, etc.)';
COMMENT ON COLUMN proposals.quality_suggestions IS 'Improvement suggestions';
