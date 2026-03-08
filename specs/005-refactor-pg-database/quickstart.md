# Quickstart: 005-refactor-pg-database

**Branch**: `005-refactor-pg-database`

## Prerequisites

- PostgreSQL running (Docker or local)
- Migrations 001–010 applied
- Backend and frontend dev environments set up

## Running the Migration

```bash
# From repo root
cd database
psql $DATABASE_URL -f migrations/011_refactor_jobs_to_projects.sql
```

Or use your migration runner (e.g., Flyway, Alembic, or manual psql).

## Verification

```sql
-- Confirm jobs renamed to projects
SELECT COUNT(*) FROM projects;

-- Confirm legacy tables dropped
SELECT tablename FROM pg_tables WHERE schemaname = 'public' AND tablename IN ('jobs', 'projects', 'bids');
-- Should return only 'projects' (the new one, renamed from jobs)

-- Confirm FKs
SELECT conname FROM pg_constraint WHERE conrelid = 'user_project_status'::regclass;
SELECT conname FROM pg_constraint WHERE conrelid = 'proposals'::regclass;
```

## After Migration

1. **Backend**: Restart backend. Ensure `project_service` (or updated `job_service`) uses `projects` table.
2. **Seed**: Run `database/seed/dev_data.sql` (updated to use new schema).
3. **Frontend**: No frontend restart needed if API unchanged.
4. **Docs**: `docs/database-schema-reference.md` updated per spec.

## Rollback (Manual)

If rollback is needed before code deploy:

1. Rename `projects` → `jobs`
2. Rename `user_project_status` → `user_job_status`
3. Alter `project_id` → `job_id` in both tables
4. Recreate `projects` and `bids` from migration 001/003 (if data needed)
5. Revert code changes

**Note**: Rollback is complex if ETL has written new data to `projects`. Prefer forward fix.
