# Research: PostgreSQL Database Refactor for UI Alignment

**Feature**: 005-refactor-pg-database  
**Date**: 2026-03-07

## 1. Table Naming: jobs vs projects

**Decision**: Rename `jobs` table to `projects` to match the Projects nav.

**Rationale**:
- UI sidebar shows "Projects" (route `/projects`). Users and developers expect the Projects page to read from a `projects` table.
- The current `jobs` table is the source of truth for the Projects UI (job_service, list_projects API).
- The legacy `projects` table (from migration 001/006) is unused by the application—only referenced in seed data and by the deprecated `bids` table.
- Aligning table name with nav reduces cognitive load and prevents future developers from using the wrong table.

**Alternatives considered**:
- **Keep jobs, rename UI to "Jobs"**: Rejected—"Projects" is more user-friendly in freelance context; users think in terms of "projects" not "jobs."
- **Add DB view `projects` as alias for jobs**: Rejected—adds indirection; direct rename is simpler.
- **Merge old projects + jobs into one table**: Rejected—schemas are incompatible (user-scoped vs ETL-fed); old projects has no production data.

---

## 2. Bids vs Proposals Consolidation

**Decision**: Remove `bids` table. Use `proposals` as the single table for user-created proposals.

**Rationale**:
- Proposals UI uses `proposals` table (proposal_service, list_proposals API).
- `bids` is linked to legacy `projects`; `proposals` is linked to `jobs` (soon `projects`).
- Both represent the same concept: a user's bid/proposal for a job opportunity.
- No production data in `bids`—only seed data. Migrating seed is trivial (or we drop seed for bids).

**Alternatives considered**:
- **Merge bids into proposals**: Would require schema reconciliation. Proposals already has job_id, strategy_id, etc. Simpler to drop bids.
- **Keep both for different workflows**: Rejected—spec requires single primary table (FR-002).

---

## 3. Legacy projects Table

**Decision**: Drop the legacy `projects` table.

**Rationale**:
- Not used by Projects UI. Projects page reads from `jobs` (via job_service).
- Only used by: (a) seed script (dev_data.sql), (b) `bids` table (project_id FK).
- Dropping `bids` first, then `projects`, clears the dependency.

**Alternatives considered**:
- **Migrate old projects data into jobs**: Not needed—no production data; seed can be rewritten.

---

## 4. etl_runs Retention

**Decision**: Retain `etl_runs` table as-is. No nav mapping required.

**Rationale**:
- Backend audit trail for ETL executions. Not a user-facing concept.
- Spec FR-004 explicitly requires retention.
- Column names reference "jobs" (jobs_inserted, jobs_updated)—acceptable; they describe ETL counts. Optional: rename to projects_inserted/projects_updated in a follow-up for consistency.

---

## 5. scraping_jobs and platform_credentials

**Decision**: Retain both tables. Do not remove.

**Rationale**:
- `scraping_jobs`: No application code references it. Documented in docs/web-scraping-status.md as future use. Retain for planned scraping features.
- `platform_credentials`: Used for Upwork/Freelancer API keys. Settings nav may use it. Retain.

---

## 6. Migration Strategy

**Decision**: Single migration file (011) with ordered steps: drop bids → drop projects → rename jobs → projects → update FKs (user_job_status, proposals) → update triggers/indexes.

**Rationale**:
- PostgreSQL `ALTER TABLE ... RENAME TO` is fast and does not rewrite data.
- FK updates: `user_job_status.job_id` → `project_id` (FK to projects); `proposals.job_id` → `project_id`.
- Enums (job_platform, job_category, job_status) can remain—they describe the entity; renaming to project_* is optional and can be deferred.

**Alternatives considered**:
- **Multi-migration approach**: More granular but adds complexity. Single migration is acceptable for this scope.
- **Zero-downtime blue-green**: Overkill for this refactor; brief maintenance window acceptable.

---

## 7. Code Update Scope

**Decision**: Update all references from `jobs`/`job_` to `projects`/`project_` in:
- backend: job_service.py, job models, ETL scripts, routers
- frontend: API client types (Project already used in UI; ensure consistency)
- database: seed script, migrations
- docs: database-schema-reference.md

**Rationale**:
- Spec FR-005 requires all code updated.
- Consistent naming across stack prevents bugs.
