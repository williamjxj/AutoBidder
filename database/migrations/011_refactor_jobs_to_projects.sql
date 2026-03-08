-- Migration 011: Refactor jobs → projects for UI alignment
-- Created: 2026-03-07
-- Description: Rename jobs to projects, drop legacy projects/bids, align table names with UI nav
-- Reference: specs/005-refactor-pg-database/spec.md, contracts/schema-migration.md

-- ============================================================
-- Step 1: Drop bids (FK to projects)
-- ============================================================
DROP TABLE IF EXISTS bids CASCADE;

-- ============================================================
-- Step 2: Drop legacy projects table
-- ============================================================
DROP TABLE IF EXISTS projects CASCADE;

-- ============================================================
-- Step 3: Rename jobs → projects
-- ============================================================
ALTER TABLE jobs RENAME TO projects;

-- ============================================================
-- Step 4: Rename user_job_status → user_project_status
-- ============================================================
ALTER TABLE user_job_status RENAME TO user_project_status;

-- ============================================================
-- Step 5: Rename job_id → project_id in user_project_status
-- ============================================================
ALTER TABLE user_project_status RENAME COLUMN job_id TO project_id;

-- ============================================================
-- Step 6: Rename job_id → project_id in proposals
-- ============================================================
ALTER TABLE proposals RENAME COLUMN job_id TO project_id;

-- ============================================================
-- Step 7: Rename user_job_qualifications → user_project_qualifications
-- (Only if migration 010 was applied)
-- ============================================================
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'user_job_qualifications') THEN
    ALTER TABLE user_job_qualifications RENAME TO user_project_qualifications;
    ALTER TABLE user_project_qualifications RENAME COLUMN job_id TO project_id;
  END IF;
END $$;

-- ============================================================
-- Step 8: Update triggers on projects (was jobs)
-- ============================================================
DROP TRIGGER IF EXISTS update_jobs_updated_at ON projects;
CREATE TRIGGER update_projects_updated_at
    BEFORE UPDATE ON projects
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_user_job_status_updated_at ON user_project_status;
CREATE TRIGGER update_user_project_status_updated_at
    BEFORE UPDATE ON user_project_status
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- Step 9: Rename indexes (jobs → projects, user_job_status → user_project_status)
-- ============================================================
ALTER INDEX IF EXISTS idx_jobs_platform RENAME TO idx_projects_platform;
ALTER INDEX IF EXISTS idx_jobs_category RENAME TO idx_projects_category;
ALTER INDEX IF EXISTS idx_jobs_status RENAME TO idx_projects_status;
ALTER INDEX IF EXISTS idx_jobs_posted_at RENAME TO idx_projects_posted_at;
ALTER INDEX IF EXISTS idx_jobs_fingerprint RENAME TO idx_projects_fingerprint;
ALTER INDEX IF EXISTS idx_jobs_skills RENAME TO idx_projects_skills;
ALTER INDEX IF EXISTS idx_jobs_fulltext RENAME TO idx_projects_fulltext;

ALTER INDEX IF EXISTS idx_user_job_status_user_id RENAME TO idx_user_project_status_user_id;
ALTER INDEX IF EXISTS idx_user_job_status_job_id RENAME TO idx_user_project_status_project_id;
ALTER INDEX IF EXISTS idx_user_job_status_status RENAME TO idx_user_project_status_status;

-- Only if user_project_qualifications exists (from migration 010)
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_user_job_qualifications_user_id') THEN
    ALTER INDEX idx_user_job_qualifications_user_id RENAME TO idx_user_project_qualifications_user_id;
  END IF;
  IF EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_user_job_qualifications_job_id') THEN
    ALTER INDEX idx_user_job_qualifications_job_id RENAME TO idx_user_project_qualifications_project_id;
  END IF;
END $$;

-- Rename proposals index (job_id → project_id)
DROP INDEX IF EXISTS idx_proposals_job_id;
CREATE INDEX IF NOT EXISTS idx_proposals_project_id ON proposals(project_id);

-- ============================================================
-- Step 10: Add increment_strategy_use trigger on proposals
-- (replaces trigger that was on bids)
-- ============================================================
-- (increment_strategy_use on bids was dropped with bids table)
DROP TRIGGER IF EXISTS increment_strategy_use_proposals ON proposals;
CREATE TRIGGER increment_strategy_use_proposals
    AFTER INSERT ON proposals
    FOR EACH ROW
    WHEN (NEW.strategy_id IS NOT NULL)
    EXECUTE FUNCTION increment_strategy_use_count();

-- ============================================================
-- Step 11: Update comments
-- ============================================================
COMMENT ON TABLE projects IS 'Job listings from ETL (HuggingFace, Freelancer) - backs Projects nav';
COMMENT ON TABLE user_project_status IS 'Per-user pipeline status (reviewed, applied, won, lost)';
-- Only if user_project_qualifications exists
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'user_project_qualifications') THEN
    EXECUTE 'COMMENT ON TABLE user_project_qualifications IS ''Per-user qualification scores for projects''';
  END IF;
END $$;
COMMENT ON COLUMN proposals.project_id IS 'Links proposal to project from Projects page';
