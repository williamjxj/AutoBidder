-- Migration 016: Remove scoring artifacts
-- Created: 2026-03-13
-- Description: Drops deprecated score-related columns, tables, and indexes.

-- ============================================================
-- PROPOSALS: remove proposal quality fields
-- ============================================================
ALTER TABLE proposals
  DROP COLUMN IF EXISTS quality_score,
  DROP COLUMN IF EXISTS quality_breakdown,
  DROP COLUMN IF EXISTS quality_suggestions;

-- ============================================================
-- USER_PROFILES: remove score-threshold fields
-- ============================================================
ALTER TABLE user_profiles
  DROP COLUMN IF EXISTS qualification_threshold,
  DROP COLUMN IF EXISTS notification_threshold,
  DROP COLUMN IF EXISTS auto_generate_threshold;

-- ============================================================
-- AUTONOMOUS_RUNS: remove qualification counter
-- ============================================================
ALTER TABLE autonomous_runs
  DROP COLUMN IF EXISTS jobs_qualified;

-- ============================================================
-- DROP score qualification tables
-- ============================================================
DROP TABLE IF EXISTS user_project_qualifications CASCADE;
DROP TABLE IF EXISTS user_job_qualifications CASCADE;

-- ============================================================
-- DROP scoring indexes if present
-- ============================================================
DROP INDEX IF EXISTS idx_upq_user_project;
DROP INDEX IF EXISTS idx_upq_score;
DROP INDEX IF EXISTS idx_upq_updated;
DROP INDEX IF EXISTS idx_upq_user_score;
DROP INDEX IF EXISTS idx_upq_stale_scores;
DROP INDEX IF EXISTS idx_user_project_qualifications_user_id;
DROP INDEX IF EXISTS idx_user_project_qualifications_project_id;
DROP INDEX IF EXISTS idx_user_job_qualifications_user_id;
DROP INDEX IF EXISTS idx_user_job_qualifications_job_id;
