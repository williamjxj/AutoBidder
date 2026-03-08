# Schema Migration Contract: 005-refactor-pg-database

**Migration file**: `database/migrations/011_refactor_jobs_to_projects.sql`  
**Rollback**: Not automated; manual reverse migration if needed

## Before → After

| Before                    | After                         |
|---------------------------|-------------------------------|
| jobs                      | **projects** (renamed)        |
| user_job_status.job_id   | user_project_status.project_id |
| proposals.job_id         | proposals.project_id         |
| projects (legacy)        | **DROPPED**                   |
| bids                      | **DROPPED**                   |

## Migration Steps (Order)

1. Drop `bids` table (FK to projects)
2. Drop `projects` table (legacy)
3. Rename `jobs` → `projects`
4. Rename `user_job_status` → `user_project_status`
5. Alter `user_project_status.job_id` → `project_id` (FK to projects)
6. Alter `proposals.job_id` → `project_id` (FK to projects)
7. Update triggers: `update_jobs_updated_at` → `update_projects_updated_at`
8. Update indexes: `idx_jobs_*` → `idx_projects_*`, `idx_user_job_status_*` → `idx_user_project_status_*`
9. Drop trigger `increment_strategy_use` on bids (table removed); add equivalent trigger on `proposals` for strategy use count
10. Update comments

## API Contract Impact

**None**. Routes `/api/projects/list`, `/api/projects/discover`, etc. remain unchanged. Response shape unchanged. Backend table names are internal.

## Code Update Checklist

- [x] backend/app/services/job_service.py → project_service.py (or keep name, update table refs)
- [x] backend/app/models/job.py → project.py (or merge into existing project.py)
- [x] backend/app/etl/* — update INSERT/SELECT table names
- [x] backend/app/routers/projects.py — ensure uses project_service
- [x] database/seed/dev_data.sql — remove projects, bids; seed projects (from jobs schema) if needed
- [x] docs/database-schema-reference.md — full rewrite with nav mapping
- [x] frontend/src/types/database.ts — remove projects, bids types if present
- [x] All SQL: jobs → projects, user_job_status → user_project_status, job_id → project_id
