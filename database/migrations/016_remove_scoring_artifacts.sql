-- Migration 016: Remove scoring artifacts
-- Created: 2026-03-13
-- Description: Consolidated cleanup migration (scoring removal + HF token normalization + proposal title split).

BEGIN;

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

-- ============================================================
-- PROPOSALS: normalize legacy HuggingFace platform tokens
-- ============================================================
UPDATE proposals
SET job_platform = 'huggingface_dataset'
WHERE job_platform IS NOT NULL
  AND LOWER(TRIM(job_platform)) IN ('hf_dataset', 'huggingface', 'hugging face');

-- ============================================================
-- PROPOSALS: separate immutable project title and editable proposal title
-- ============================================================
ALTER TABLE proposals
  ADD COLUMN IF NOT EXISTS project_title VARCHAR(500),
  ADD COLUMN IF NOT EXISTS proposal_title VARCHAR(500);

UPDATE proposals
SET proposal_title = COALESCE(NULLIF(TRIM(proposal_title), ''), title)
WHERE proposal_title IS NULL OR TRIM(proposal_title) = '';

UPDATE proposals p
SET project_title = pr.title
FROM projects pr
WHERE p.project_id = pr.id
  AND (p.project_title IS NULL OR TRIM(p.project_title) = '');

UPDATE proposals
SET project_title = COALESCE(NULLIF(TRIM(project_title), ''), proposal_title)
WHERE project_title IS NULL OR TRIM(project_title) = '';

COMMIT;
