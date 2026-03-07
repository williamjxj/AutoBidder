# Tasks: Autonomous Bidding Improvements

**Input**: Design documents from `/specs/004-improve-autonomous/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1–US6)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/app/`, `backend/tests/`
- **Frontend**: `frontend/src/`
- **Database**: `database/migrations/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Dependencies and environment for autonomous features

- [x] T001 Add SendGrid to backend/requirements.txt and backend/pyproject.toml
- [x] T002 [P] Add autonomy-related env vars to backend/.env.example (AUTO_DISCOVERY_ENABLED, SENDGRID_API_KEY, AUTO_PROPOSAL_THRESHOLD)
- [x] T003 [P] Add SENDGRID_API_KEY and AUTO_DISCOVERY_ENABLED to backend/app/config.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Schema and autonomy settings API—required before any user story

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Create database/migrations/010_autonomous_settings.sql with user_profiles columns (auto_discovery_enabled, discovery_interval_minutes, qualification_threshold, notification_threshold, notifications_enabled, auto_generate_enabled, auto_generate_threshold, autonomy_level)
- [x] T005 Add user_job_qualifications table and autonomous_runs table in database/migrations/010_autonomous_settings.sql
- [x] T006 Add proposals extensions (source, auto_generated_at, quality_score, quality_breakdown, quality_suggestions) in database/migrations/010_autonomous_settings.sql
- [x] T007 [P] Create backend/app/services/autonomy_settings_service.py to read/write user_profiles autonomy columns
- [x] T008 Implement GET /api/autonomous/settings and PUT /api/autonomous/settings in backend/app/routers/autonomous.py (or extend settings router)
- [x] T009 Register autonomous router in backend/app/main.py with prefix /api/autonomous
- [x] T010 [P] Create backend/app/models/autonomy.py with AutonomousSettings and AutonomousSettingsUpdate Pydantic models

**Checkpoint**: Migration applied; autonomy settings API returns/updates user preferences

---

## Phase 3: User Story 1 - Automatic Job Discovery (Priority: P1) 🎯 MVP

**Goal**: Jobs auto-discovered every 15 minutes for users with auto-discovery enabled

**Independent Test**: Enable auto-discovery for a user, wait for interval (or trigger manually), verify new jobs appear in dashboard without manual Discover click

### Implementation for User Story 1

- [x] T011 [US1] Create backend/app/tasks/autonomous_tasks.py with async def run_autonomous_discovery_for_user(user_id) that fetches keywords via keyword_service, calls hf_loader or hf_job_source, upserts jobs via job_service
- [x] T012 [US1] Add run_autonomous_discovery_job() in backend/app/tasks/autonomous_tasks.py that queries user_profiles WHERE auto_discovery_enabled=true and invokes run_autonomous_discovery_for_user per user
- [x] T013 [US1] Extend backend/app/etl/scheduler.py to add autonomous discovery job (IntervalTrigger minutes=15) when AUTO_DISCOVERY_ENABLED=true
- [x] T014 [US1] Call start_autonomous_scheduler or equivalent from backend/app/main.py startup when AUTO_DISCOVERY_ENABLED=true
- [x] T015 [US1] Add per-user try/except in run_autonomous_discovery_job so one user's failure does not block others (FR-012)

**Checkpoint**: Auto-discovery runs on schedule; new jobs appear for users with auto_discovery_enabled=true

---

## Phase 4: User Story 2 - Intelligent Job Qualification (Priority: P1)

**Goal**: Jobs scored and filtered by skill match, budget fit; only qualified jobs shown

**Independent Test**: Discover jobs, run qualification, verify only jobs above threshold appear with scores

### Implementation for User Story 2

- [x] T016 [P] [US2] Create backend/app/services/qualification_service.py with score_job(job, user_profile) using Jaccard skill match (50%), budget fit (30%), client quality placeholder (20%)
- [x] T017 [US2] Add score_and_filter_jobs(user_id, jobs, min_score) in backend/app/services/qualification_service.py returning qualified jobs with qualification_score and qualification_reason
- [x] T018 [US2] Add upsert_user_job_qualification(user_id, job_id, score, reason) in backend/app/services/qualification_service.py writing to user_job_qualifications
- [x] T019 [US2] Integrate qualification into autonomous pipeline: after discovery, call qualification_service for each user's discovered jobs, persist scores
- [x] T020 [US2] Extend backend/app/services/job_service.py or projects router to return qualification_score and qualification_reason when listing jobs for a user (join user_job_qualifications)

**Checkpoint**: Qualified jobs display scores; only jobs above threshold in qualified list

---

## Phase 5: User Story 3 - Smart Notifications for Qualified Jobs (Priority: P2)

**Goal**: Email notification when high-quality jobs (e.g., ≥80%) found

**Independent Test**: Trigger qualification with high-score jobs, verify email sent when notifications_enabled and score ≥ threshold

### Implementation for User Story 3

- [x] T021 [P] [US3] Create backend/app/services/notification_service.py with notify_qualified_jobs(user_email, qualified_jobs, threshold) using SendGrid
- [x] T022 [US3] Add graceful fallback in notification_service when SENDGRID_API_KEY not set (log, skip, do not block pipeline)
- [x] T023 [US3] Integrate notification into autonomous pipeline: after qualification, if user has notifications_enabled and any job score ≥ notification_threshold, call notification_service
- [x] T024 [US3] Fetch user email from users table when sending notifications (join user_profiles + users)

**Checkpoint**: High-quality job matches trigger email when notifications enabled

---

## Phase 6: User Story 4 - Auto-Generate Proposals for High-Confidence Matches (Priority: P2)

**Goal**: Proposal drafts auto-generated for jobs ≥85% match when auto_generate_enabled

**Independent Test**: Qualify jobs above auto_generate_threshold, verify proposals created with source=auto_generated

### Implementation for User Story 4

- [x] T025 [P] [US4] Create backend/app/services/auto_proposal_service.py with auto_generate_proposals(user_id, qualified_jobs, threshold) calling ai_service.generate_proposal per job
- [x] T026 [US4] Save auto-generated proposals with source='auto_generated', auto_generated_at=NOW(), generated_with_ai=true in backend/app/services/auto_proposal_service.py
- [x] T027 [US4] Integrate auto_proposal_service into autonomous pipeline: after qualification, for jobs ≥ auto_generate_threshold and auto_generate_enabled, call auto_generate_proposals
- [x] T028 [US4] Use user's default bidding_strategy for auto-generation (strategy_service or settings)
- [x] T029 [US4] Ensure proposals list/detail API returns source and auto_generated_at for frontend to show "Auto-generated" badge (FR-008)

**Checkpoint**: High-confidence jobs get auto-generated proposal drafts; UI shows badge

---

## Phase 7: User Story 5 - Proposal Quality Feedback (Priority: P3)

**Goal**: Quality score (0–100) and improvement suggestions for each generated proposal

**Independent Test**: Generate proposal, verify quality_score and suggestions displayed

### Implementation for User Story 5

- [x] T030 [P] [US5] Create backend/app/services/proposal_quality_service.py with score_proposal(proposal_text, job_description, job_requirements) returning overall_score, dimension_scores, suggestions
- [x] T031 [US5] Implement dimension scoring (length, coverage, citations, grammar, personalization) per quick-wins doc in backend/app/services/proposal_quality_service.py
- [x] T032 [US5] Call proposal_quality_service after ai_service.generate_proposal and persist quality_score, quality_breakdown, quality_suggestions on proposals
- [x] T033 [US5] Add GET /api/proposals/{proposal_id}/quality endpoint in backend/app/routers/proposals.py (or autonomous router) returning ProposalQuality schema
- [x] T034 [US5] Extend frontend proposal detail view to display quality score and suggestions (frontend component for proposals)

**Checkpoint**: Proposals show quality score and actionable suggestions

---

## Phase 8: User Story 6 - Configurable Autonomy Level (Priority: P3)

**Goal**: User chooses autonomy level (discovery only, semi-autonomous, full auto-generate)

**Independent Test**: Change autonomy level in settings, verify pipeline behavior matches (e.g., discovery_only skips qualification/auto-gen)

### Implementation for User Story 6

- [x] T035 [US6] Implement autonomy_level behavior in run_autonomous_discovery_for_user: assisted/discovery_only = discovery only; semi_autonomous = discovery + qualify + notify + auto-gen (if enabled); full_auto_generate = same
- [x] T036 [US6] Add autonomy settings UI section to frontend/src/app/(dashboard)/settings/page.tsx with toggles for auto_discovery_enabled, notifications_enabled, auto_generate_enabled, and dropdown for autonomy_level
- [x] T037 [US6] Add threshold sliders (qualification_threshold, notification_threshold, auto_generate_threshold) and discovery_interval_minutes input in settings UI
- [x] T038 [US6] Wire settings UI to GET/PUT /api/autonomous/settings (or /api/settings/autonomy) with proper error handling

**Checkpoint**: User can configure autonomy; pipeline respects settings

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Audit trail, status API, tests, documentation

- [x] T039 Implement autonomous_runs recording: create row at pipeline start, update on completion with jobs_discovered, jobs_qualified, proposals_generated, notifications_sent, errors
- [x] T040 Implement GET /api/autonomous/status returning last_run_at, status, jobs_discovered, jobs_qualified, proposals_auto_generated, notifications_sent, errors from autonomous_runs
- [x] T041 Implement POST /api/autonomous/run to trigger manual run (background task) returning run_id and status=started
- [x] T042 [P] Add unit test backend/tests/unit/services/test_qualification_service.py for score_job and score_and_filter_jobs
- [x] T043 [P] Add unit test backend/tests/unit/services/test_auto_proposal_service.py for auto_generate_proposals
- [x] T044 Add integration test backend/tests/integration/test_autonomous_flow.py for discovery → qualification → notification → auto-generate pipeline
- [x] T045 Run quickstart.md validation: migration, env, manual trigger, status check

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies
- **Phase 2 (Foundational)**: Depends on Phase 1 — BLOCKS all user stories
- **Phase 3 (US1)**: Depends on Phase 2
- **Phase 4 (US2)**: Depends on Phase 2; integrates with US1 pipeline
- **Phase 5 (US3)**: Depends on Phase 2, 4 (qualification produces qualified jobs)
- **Phase 6 (US4)**: Depends on Phase 2, 4
- **Phase 7 (US5)**: Depends on Phase 2; can run in parallel with US4
- **Phase 8 (US6)**: Depends on Phase 2; UI can be built after API (T008)
- **Phase 9 (Polish)**: Depends on Phases 3–8

### User Story Dependencies

| Story | Depends On | Can Start After |
|-------|------------|-----------------|
| US1 | Phase 2 | Foundational complete |
| US2 | Phase 2 | Foundational complete |
| US3 | Phase 2, US2 | Qualification service exists |
| US4 | Phase 2, US2 | Qualification service exists |
| US5 | Phase 2 | Foundational complete |
| US6 | Phase 2 | Foundational complete (API); UI after T008 |

### Parallel Opportunities

- T002, T003 can run in parallel (Phase 1)
- T007, T010 can run in parallel (Phase 2)
- T016, T021, T025, T030 can run in parallel (different services)
- T042, T043 can run in parallel (Phase 9)

---

## Parallel Example: Phase 2

```bash
# After T004–T006 (migration), these can run in parallel:
Task T007: "Create autonomy_settings_service.py"
Task T010: "Create autonomy Pydantic models"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (migration + autonomy settings API)
3. Complete Phase 3: User Story 1 (auto-discovery scheduler)
4. **STOP and VALIDATE**: Enable auto-discovery, wait/trigger, verify jobs appear
5. Deploy/demo

### Incremental Delivery

1. Setup + Foundational → Settings API ready
2. US1 → Auto-discovery working (MVP)
3. US2 → Qualification filters jobs
4. US3 → Notifications for high-quality matches
5. US4 → Auto-generated proposals
6. US5 → Quality feedback on proposals
7. US6 → Full settings UI
8. Polish → Status API, tests, docs

### Suggested MVP Scope

**Phases 1 + 2 + 3** = Minimum viable autonomous system: users enable auto-discovery, jobs appear automatically. Total: ~15 tasks (T001–T015).

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to user story for traceability
- Each user story is independently testable per spec acceptance scenarios
- Migration 010 is additive; safe to apply without breaking existing features
- SendGrid optional: pipeline continues if SENDGRID_API_KEY not set
