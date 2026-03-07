# Quickstart: Autonomous Bidding Improvements

**Feature**: 004-improve-autonomous  
**Branch**: `004-improve-autonomous`  
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## Prerequisites

- Python 3.12+, FastAPI backend running
- PostgreSQL with `jobs`, `user_job_status`, `proposals`, `user_profiles`, `keywords` tables
- ETL persistence enabled (`ETL_USE_PERSISTENCE=true`)
- Optional: SendGrid API key for email notifications

## Setup (5 minutes)

### 1. Run database migration

```bash
cd backend
# Apply migration 010_autonomous_settings.sql
psql $DATABASE_URL -f database/migrations/010_autonomous_settings.sql
```

### 2. Install dependencies

```bash
pip install apscheduler sendgrid  # If not already in requirements
```

### 3. Environment variables

Add to `backend/.env`:

```bash
# Autonomous (optional)
AUTO_DISCOVERY_ENABLED=true
AUTO_PROPOSAL_THRESHOLD=0.85
SENDGRID_API_KEY=your_sendgrid_key  # For notifications
```

### 4. Enable autonomous scheduler

The autonomous discovery job is started from `main.py` startup (see plan). Ensure `start_autonomous_scheduler()` is called when `AUTO_DISCOVERY_ENABLED=true`.

## Verify

1. **Settings API**: `GET /api/autonomous/settings` (with JWT) returns default autonomy settings.
2. **Manual run**: `POST /api/autonomous/run` triggers discovery + qualification for the current user.
3. **Status**: `GET /api/autonomous/status` shows last run stats.

## Implementation Order

| Step | Component | Location |
|------|-----------|----------|
| 1 | DB migration (user_profiles, proposals) | `database/migrations/010_autonomous_settings.sql` |
| 2 | Autonomy settings service | `backend/app/services/autonomy_settings_service.py` |
| 3 | Qualification service | `backend/app/services/qualification_service.py` |
| 4 | Notification service | `backend/app/services/notification_service.py` |
| 5 | Auto-proposal service | `backend/app/services/auto_proposal_service.py` |
| 6 | Proposal quality service | `backend/app/services/proposal_quality_service.py` |
| 7 | Autonomous scheduler + tasks | `backend/app/tasks/autonomous_tasks.py` |
| 8 | Autonomous router | `backend/app/routers/autonomous.py` |
| 9 | Settings UI (autonomy toggles) | `frontend/src/app/(dashboard)/settings/` |

## Key Files to Modify

- `backend/app/main.py` — Add `start_autonomous_scheduler()` on startup
- `backend/app/routers/settings.py` — Extend with autonomy preferences (or new autonomous router)
- `backend/app/etl/scheduler.py` — Optionally integrate autonomous job into existing scheduler

## Testing

```bash
# Unit tests
pytest backend/tests/unit/services/test_qualification_service.py -v
pytest backend/tests/unit/services/test_proposal_quality_service.py -v

# Integration (with DB)
pytest backend/tests/integration/test_autonomous_flow.py -v
```

## Rollback

1. Set `AUTO_DISCOVERY_ENABLED=false` and restart.
2. Remove `start_autonomous_scheduler()` from `main.py`.
3. Migration 010 is additive; no rollback required for schema (columns can remain).
