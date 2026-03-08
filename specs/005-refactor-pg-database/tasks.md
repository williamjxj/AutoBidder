# Tasks: Refactor PostgreSQL Database for UI Alignment

**Input**: Design documents from `/specs/005-refactor-pg-database/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/schema-migration.md, quickstart.md

**Organization**: Tasks grouped by user story. US1 and US2 are implemented together (same migration + code changes). US3 is documentation.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1, US2, US3
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify environment and migration tooling

- [x] T001 Verify PostgreSQL is running and migrations 001–010 are applied
- [x] T002 [P] Confirm no active ETL jobs or long-running queries before migration

---

## Phase 2: Foundational (Migration — Blocks All User Stories)

**Purpose**: Create and run migration 011. Achieves US1 (table rename) + US2 (drop unused tables) at schema level.

**⚠️ CRITICAL**: No code updates can proceed until migration runs successfully.

- [x] T003 Create database/migrations/011_refactor_jobs_to_projects.sql with steps: drop bids, drop projects, rename jobs→projects, rename user_job_status→user_project_status, alter job_id→project_id in user_project_status and proposals, update triggers and indexes, add increment_strategy_use trigger on proposals (replacing bids trigger)
- [x] T004 Run migration 011 against dev database and verify via quickstart.md verification queries

**Checkpoint**: Schema refactored. Tables projects, user_project_status exist. Tables jobs, projects (legacy), bids removed.

---

## Phase 3: User Story 1 & 2 — Backend Code Updates (Priority: P1)

**Goal**: Update all backend code to use new table names (projects, user_project_status, project_id). Remove references to jobs, bids, legacy projects.

**Independent Test**: Backend starts without errors; GET /api/projects/list returns data; proposals API works.

- [x] T005 [US1] [US2] Rename backend/app/services/job_service.py to project_service.py and update all SQL: jobs→projects, user_job_status→user_project_status, job_id→project_id
- [x] T006 [US1] [US2] Update backend/app/models/job.py: rename to project.py or merge into existing project.py; update table/column references
- [x] T007 [US1] [US2] Update backend/app/etl/hf_loader.py and backend/app/etl/domain_filter.py: INSERT/SELECT from projects table
- [x] T008 [US1] [US2] Update backend/app/etl/scheduler.py and backend/scripts/hf_etl.py, backend/scripts/freelancer_etl.py: upsert to projects, record_etl_run references
- [x] T009 [US1] [US2] Update backend/app/routers/projects.py: import project_service (or job_service with updated refs), ensure list_projects/discover use projects table
- [x] T010 [US1] [US2] Update backend/app/routers/etl.py if it references jobs table
- [x] T011 [US1] [US2] Update backend/app/services/proposal_service.py: job_id→project_id in queries
- [x] T012 [US1] [US2] Update backend/app/services/autonomy_settings_service.py and backend/app/tasks/autonomous_tasks.py: job/project references
- [x] T013 [US1] [US2] Update backend/main.py and any router imports: job_service→project_service if renamed
- [x] T014 [US1] [US2] Update backend/tests/integration/test_projects_api.py and backend/tests/unit/*: jobs→projects, user_job_status→user_project_status

**Checkpoint**: Backend uses new schema. No references to jobs, bids, legacy projects in backend code.

---

## Phase 4: User Story 2 — Seed & Frontend (Priority: P1)

**Goal**: Update seed script and frontend types. Remove projects/bids from seed; ensure frontend has no stale types.

**Independent Test**: Run dev_data.sql without errors; frontend builds; Projects and Proposals pages load.

- [x] T016 [US2] Update database/seed/dev_data.sql: remove INSERT into projects and bids; add seed for projects table (ETL schema) if needed for dev; update TRUNCATE list
- [x] T017 [US2] Update frontend/src/types/database.ts: remove or update projects, bids type definitions; ensure Project type maps to new schema
- [x] T018 [US2] [P] Grep frontend for references to bids or legacy projects; update if any found in frontend/src/

**Checkpoint**: Seed runs cleanly. Frontend has no references to dropped tables.

---

## Phase 5: User Story 3 — Documentation (Priority: P2)

**Goal**: docs/database-schema-reference.md accurately reflects final schema with nav-to-table mapping.

**Independent Test**: Read docs/database-schema-reference.md; each nav item maps to table(s); no mention of jobs, bids, legacy projects.

- [x] T019 [US3] Rewrite docs/database-schema-reference.md: add Nav-to-Table Mapping section (from data-model.md), update Table Overview, remove projects and bids from table list, update ER diagram, add Resources/Bidders groups
- [x] T020 [US3] [P] Update docs/web-scraping-status.md if it references projects/bids schema

**Checkpoint**: Documentation is accurate and complete.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final verification and cleanup

- [x] T021 Run quickstart.md verification steps end-to-end
- [x] T022 [P] Run backend tests: pytest backend/tests/
- [x] T023 [P] Run frontend build: cd frontend && npm run build
- [x] T024 Verify Projects page: discover jobs, list projects, generate proposal flow works
- [x] T025 Update specs/005-refactor-pg-database/contracts/schema-migration.md code checklist: mark all items complete

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies
- **Phase 2 (Migration)**: Depends on Phase 1 — BLOCKS Phases 3–5
- **Phase 3 (Backend)**: Depends on Phase 2
- **Phase 4 (Seed/Frontend)**: Depends on Phase 2; can run in parallel with Phase 3 after T006–T010
- **Phase 5 (Docs)**: Depends on Phase 2; can run in parallel with Phase 3–4
- **Phase 6 (Polish)**: Depends on Phases 3, 4, 5

### User Story Dependencies

- **US1 + US2**: Implemented together in Phases 2–4 (migration + code)
- **US3**: Phase 5; can start after Phase 2 (docs can be written once schema is known)

### Parallel Opportunities

- T002 can run in parallel with T001
- T019 and T020 can run in parallel
- T022 and T023 can run in parallel
- Backend tasks T006–T015 are mostly sequential (same files); T008, T009 can run in parallel (different ETL files)

---

## Parallel Example: After Migration

```bash
# Once Phase 2 completes, these can run in parallel:
# Backend: T006 (job_service) 
# Backend: T007 (models)
# Backend: T008, T009 (ETL - different files)
# Docs: T019 (database-schema-reference.md)
```

---

## Implementation Strategy

### MVP First (US1 + US2)

1. Phase 1: Setup
2. Phase 2: Migration 011
3. Phase 3: Backend code updates
4. Phase 4: Seed + frontend
5. **STOP and VALIDATE**: Projects page, Proposals page, ETL discover work
6. Phase 5: Documentation
7. Phase 6: Polish

### Incremental Delivery

1. Phase 1 + 2 → Schema refactored
2. Phase 3 + 4 → App works with new schema (MVP!)
3. Phase 5 → Docs updated
4. Phase 6 → Full verification

---

## Notes

- Migration 011 must be run before any code changes; code expects new schema
- job_service can be renamed to project_service or kept as job_service with updated table refs (plan allows either)
- increment_strategy_use trigger: was on bids; add to proposals in migration 011
- No new test tasks per spec (tests not explicitly requested); existing tests must pass after updates
