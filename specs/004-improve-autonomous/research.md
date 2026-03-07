# Research: Autonomous Bidding Improvements

**Branch**: 004-improve-autonomous  
**Date**: 2026-03-07  
**Purpose**: Resolve technical decisions for autonomous discovery, qualification, notifications, and auto-generation

---

## 1. Background Job Scheduler

**Decision**: Use APScheduler (AsyncIOScheduler) for autonomous discovery and qualification.

**Rationale**:
- APScheduler is already used for ETL (HF + Freelancer) in `app/etl/scheduler.py`
- In-process scheduler avoids Redis/Celery infrastructure for quick wins
- AsyncIOScheduler supports async functions natively
- Same process = shared DB pool, no serialization overhead

**Alternatives considered**:
- **Celery + Redis**: Better for distributed workers and retries; overkill for Phase 1. Can migrate later per autonomous-implementation-guide.
- **Cron + CLI**: Requires external process; less integrated with FastAPI lifecycle.

**Implementation**: Add a new scheduled job `auto_discovery` to the existing scheduler, triggered every 15 minutes (configurable). Reuse `_run_hf_ingestion_job` pattern.

---

## 2. User Autonomy Settings Storage

**Decision**: Extend `user_profiles` with new columns for autonomy settings.

**Rationale**:
- `user_profiles` already stores `preferences` JSONB (notification_email, theme, etc.)
- Autonomy settings are user preferences; belong in user_profiles
- New columns allow indexed queries (e.g., `WHERE auto_discovery_enabled = true`) for scheduler efficiency
- Avoids deep JSONB queries for hot path

**Schema additions** (migration):
```sql
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS
  auto_discovery_enabled BOOLEAN DEFAULT false,
  discovery_interval_minutes INTEGER DEFAULT 15,
  qualification_threshold NUMERIC(3,2) DEFAULT 0.60,
  notification_threshold NUMERIC(3,2) DEFAULT 0.80,
  auto_generate_threshold NUMERIC(3,2) DEFAULT 0.85,
  autonomy_level VARCHAR(20) DEFAULT 'assisted' CHECK (autonomy_level IN ('assisted','semi_autonomous','full_auto_generate'));
```

**Alternatives considered**:
- **preferences JSONB only**: Works but requires JSONB queries; less efficient for scheduler.
- **New autonomy_settings table**: Over-normalization; one row per user, better as columns.

---

## 3. Keywords Source for Auto-Discovery

**Decision**: Use `keywords` table (user-owned) for discovery; fallback to `preferences` or empty list.

**Rationale**:
- `keywords` table already exists and is used by `POST /api/projects/discover` (keyword_service.list_keywords)
- Each user has their own keywords; `keyword_service` returns active keywords
- No new tables needed

**Implementation**: In auto_discovery job, for each user with `auto_discovery_enabled=true`, call `keyword_service.list_keywords(user_id, is_active=True)` to get keywords. If none, skip or use safe default (e.g., empty → no discovery for that user).

---

## 4. Job Qualification Scoring

**Decision**: Rule-based scoring (skill match, budget fit) without ML for Phase 1.

**Rationale**:
- Quick wins doc specifies simple Jaccard similarity for skills, budget comparison
- No training data or model deployment required
- Sufficient for 60%+ qualification accuracy target
- ML win-probability can be added in Phase 7 (Learning Agent)

**Scoring formula** (from quick-wins):
- Skill match: 50% (Jaccard similarity job_skills vs user skills)
- Budget fit: 30% (job_budget_min >= user min_project_budget)
- Client quality: 20% (placeholder 0.7 until client data available)

**User skills source**: `keywords` table has keyword text; for skills we need a dedicated field. **Sub-decision**: Add `skills` to `user_profiles.preferences` JSONB or new column. Prefer `preferences->'skills'` array for now to avoid migration; can add `user_profiles.skills TEXT[]` later.

---

## 5. Notification Delivery

**Decision**: SendGrid for email notifications; optional (feature works without it).

**Rationale**:
- Quick wins doc uses SendGrid; widely used, good deliverability
- `user_profiles.preferences` has `notification_email: true`; we can add `notification_qualified_jobs: true`
- If SENDGRID_API_KEY not set, log and skip notifications; pipeline continues

**Alternatives considered**:
- **Resend, Postmark**: Similar; SendGrid has more docs in quick-wins
- **In-app only**: Simpler but doesn't meet "wake up to opportunities" goal
- **Push notifications**: Requires frontend/device setup; defer

**Implementation**: New `app/services/notification_service.py`; inject into autonomous pipeline after qualification.

---

## 6. Proposal Auto-Generation Integration

**Decision**: Reuse existing `ai_service.generate_proposal` and `proposal_service`; add `status` and `source` to proposals.

**Rationale**:
- `proposals` table exists; `generated_with_ai` boolean already present
- Add `source` enum or column: `manual` | `auto_generated`
- `bidding_strategies` has default strategy; use user's default for auto-generation
- No new AI stack; same RAG + OpenAI flow

**Schema**: `proposals` may need `source VARCHAR` (manual, auto_generated) or use `generated_with_ai` + new column `auto_generated_at TIMESTAMPTZ` to distinguish.

---

## 7. Proposal Quality Scoring

**Decision**: LLM-based scoring (gpt-4o-mini) for length, coverage, citations, grammar, personalization.

**Rationale**:
- Quick wins doc provides concrete algorithm (weights, dimension scores)
- gpt-4o-mini is cost-effective for scoring
- Scores stored with proposal for UI display

**Storage**: Add `quality_score NUMERIC(5,2)`, `quality_suggestions JSONB` to proposals or a separate `proposal_quality` table. Prefer columns on `proposals` for simplicity.

---

## 8. Autonomy Level Behavior

**Decision**: Three levels—assisted, semi_autonomous, full_auto_generate.

**Rationale**:
- **assisted**: Discovery only (or discovery + qualification, no auto-generate)
- **semi_autonomous**: Discovery + qualification + notifications + auto-generate (proposals as drafts)
- **full_auto_generate**: Same as semi but auto-generate threshold may be lower; no auto-submit in Phase 1

**Implementation**: `autonomy_level` controls which steps run. `assisted` = discovery only. `semi_autonomous` = discovery + qualify + notify + auto-generate. `full_auto_generate` = same; name reserves future auto-submit.

---

## 9. Error Handling and Resilience

**Decision**: Per-user try/except in pipeline; one user's failure does not block others.

**Rationale**:
- Spec FR-012: "handle errors without blocking entire pipeline"
- Log failures, continue with next user
- Optionally write to `autonomous_runs` or `workflow_analytics` for observability

---

## 10. Database Migration Strategy

**Decision**: Single migration file for all autonomy-related schema changes.

**Rationale**:
- Add columns to user_profiles, proposals; keep migrations small and reversible
- Use `IF NOT EXISTS` / `ADD COLUMN IF NOT EXISTS` where supported for idempotency

---

## Summary Table

| Topic | Decision | Key Rationale |
|-------|----------|----------------|
| Scheduler | APScheduler | Already in use, in-process, async |
| User settings | user_profiles columns | Indexed, efficient for scheduler |
| Keywords | keywords table | Existing, per-user |
| Qualification | Rule-based scoring | No ML, fast to ship |
| Notifications | SendGrid | Optional, email |
| Auto-generate | Reuse ai_service | No new stack |
| Quality scoring | gpt-4o-mini | Cost-effective |
| Autonomy levels | 3 levels | assisted, semi, full |
