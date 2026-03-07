# Implementation Plan: Autonomous Bidding Improvements

**Branch**: `004-improve-autonomous` | **Date**: 2026-03-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-improve-autonomous/spec.md`

## Summary

Transform Auto-Bidder from manual discovery to autonomous job discovery, qualification, notifications, and auto-generated proposals. The approach follows the quick-wins strategy: extend the existing APScheduler and ETL pipeline with per-user autonomous discovery, add a rule-based qualification service, integrate email notifications (SendGrid), and auto-generate proposals for high-confidence matches. User autonomy settings are stored in `user_profiles` (extended) and `keywords` (existing).

## Technical Context

**Language/Version**: Python 3.12+  
**Primary Dependencies**: FastAPI, asyncpg, APScheduler, OpenAI (existing); SendGrid (new for notifications)  
**Storage**: PostgreSQL (existing: jobs, user_job_status, proposals, user_profiles, keywords)  
**Testing**: pytest (existing); add unit tests for qualification, notification, auto-proposal services  
**Target Platform**: Linux server (Docker); Next.js frontend for settings UI  
**Project Type**: Web application (backend + frontend)  
**Performance Goals**: Discovery cycle completes in under 5 minutes; qualification scoring <100ms per job  
**Constraints**: Respect ETL rate limits; notification delivery non-blocking; auto-generation limited by user threshold  
**Scale/Scope**: Multi-tenant; per-user autonomy settings; 50+ jobs discovered per user per day when sources available  

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

No project-specific constitution file found (`.specify/memory/constitution.md` is a template). Using workspace rules as guidance:

- **Python best practices**: Type annotations, docstrings, pytest, Ruff
- **Next.js/Tailwind**: Frontend settings page with shadcn/ui
- **Error handling**: Services throw user-friendly errors; early returns for edge cases

**Gates**: PASS (no explicit constitution violations)

## Project Structure

### Documentation (this feature)

```text
specs/004-improve-autonomous/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (autonomous-api.yaml)
└── tasks.md             # Phase 2 output (/speckit.tasks - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── etl/
│   │   └── scheduler.py           # Extend: add autonomous discovery job
│   ├── services/
│   │   ├── hf_job_source.py       # Existing: used by discovery
│   │   ├── job_service.py         # Existing: upsert, list jobs
│   │   ├── ai_service.py          # Existing: proposal generation
│   │   ├── qualification_service.py   # NEW: job scoring/filtering
│   │   ├── notification_service.py   # NEW: email notifications
│   │   └── auto_proposal_service.py  # NEW: auto-generate proposals
│   ├── routers/
│   │   ├── projects.py            # Existing: discover, list
│   │   └── settings.py            # Extend: autonomy settings
│   └── main.py                    # Extend: start autonomous scheduler
└── tests/
    ├── unit/
    │   └── services/
    │       ├── test_qualification_service.py
    │       └── test_auto_proposal_service.py
    └── integration/
        └── test_autonomous_flow.py

frontend/
└── src/
    └── app/
        └── (dashboard)/
            └── settings/
                └── page.tsx       # Extend: autonomy toggles, thresholds

database/
└── migrations/
    └── 010_autonomous_settings.sql  # NEW: user_profiles autonomy columns
```

**Structure Decision**: Web application. Backend extends existing FastAPI app; frontend extends settings page. New services are modular and independently testable.

## Complexity Tracking

No constitution violations requiring justification.
