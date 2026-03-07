# Data Model: Autonomous Bidding Improvements

**Feature**: 004-improve-autonomous  
**Spec**: [spec.md](./spec.md)  
**Reference**: [database-schema-reference.md](../../docs/database-schema-reference.md)

## Overview

This feature extends the existing schema to support autonomous job discovery, qualification, notifications, and auto-generated proposals. Changes are additive: new columns on `user_profiles`, optional columns on `proposals`, and a new `autonomous_runs` table for audit and monitoring.

## Entity Relationship Summary

```
┌─────────────┐     ┌──────────────────┐     ┌────────────┐
│   users     │─────│  user_profiles   │─────│  autonomy   │
│             │     │  + autonomy cols │     │  settings  │
└─────────────┘     └──────────────────┘     └────────────┘
       │                    │
       │                    │ keywords (existing)
       │                    │
       ▼                    ▼
┌─────────────┐     ┌──────────────────┐     ┌────────────┐
│  proposals  │─────│  jobs            │─────│ autonomous │
│  + quality  │     │  (existing)      │     │ _runs      │
└─────────────┘     └──────────────────┘     └────────────┘
```

## Schema Changes

### user_profiles (extend)

Add autonomy-related columns. Keywords remain in `keywords` table. **User skills** for qualification scoring are stored in `preferences` JSONB as `preferences->'skills'` (array of strings) until a dedicated column is added; budget preferences use `preferences->'min_project_budget'` or similar.

| Column | Type | Default | Description |
|--------|------|---------|-------------|
| auto_discovery_enabled | BOOLEAN | false | Run discovery for this user on schedule |
| discovery_interval_minutes | INTEGER | 15 | Minutes between discovery runs |
| qualification_threshold | NUMERIC(3,2) | 0.60 | Min score (0–1) for job to appear as qualified |
| notification_threshold | NUMERIC(3,2) | 0.80 | Min score to trigger notification |
| notifications_enabled | BOOLEAN | true | Send email when high-quality jobs found |
| auto_generate_enabled | BOOLEAN | false | Auto-generate proposals for high-confidence jobs |
| auto_generate_threshold | NUMERIC(3,2) | 0.85 | Min score to auto-generate proposal |
| autonomy_level | VARCHAR(20) | 'assisted' | assisted, semi_autonomous, fully_autonomous |

**Validation**:
- `qualification_threshold`, `notification_threshold`, `auto_generate_threshold` in [0, 1]
- `discovery_interval_minutes` in [5, 1440] (5 min to 24 hours)
- `autonomy_level` in ('assisted', 'semi_autonomous', 'fully_autonomous')

**Index**: `idx_user_profiles_auto_discovery` on `(auto_discovery_enabled)` where `auto_discovery_enabled = true` for efficient scheduler queries.

---

### jobs (extend)

Add qualification metadata when jobs are scored. Optional—can be stored in a separate `job_qualifications` table if preferred to avoid coupling.

| Column | Type | Description |
|--------|------|-------------|
| qualification_score | NUMERIC(3,2) | Fit score 0–1 (nullable until qualified) |
| qualification_reason | TEXT | Brief explanation (e.g., "Good match - worth pursuing") |

**Alternative**: Store in `user_job_qualifications(user_id, job_id, score, reason)` for per-user scores when same job is qualified for multiple users. For MVP, we can compute on-the-fly and optionally cache in a lightweight table.

**Decision**: Use `user_job_qualifications` table for per-user qualification scores (same job, different users, different scores).

---

### user_job_qualifications (new)

Per-user qualification scores for jobs. Enables "qualified for me" views without recomputing.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Primary key |
| user_id | UUID | FK users(id), NOT NULL | User |
| job_id | UUID | FK jobs(id), NOT NULL | Job |
| qualification_score | NUMERIC(3,2) | NOT NULL | 0–1 fit score |
| qualification_reason | TEXT | | Human-readable explanation |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |

**Unique**: (user_id, job_id)

---

### proposals (extend)

Add source and quality metadata for auto-generated proposals.

| Column | Type | Default | Description |
|--------|------|---------|-------------|
| source | VARCHAR(20) | 'manual' | manual, auto_generated |
| auto_generated_at | TIMESTAMPTZ | NULL | When auto-generated (if source=auto_generated) |
| quality_score | INTEGER | NULL | 0–100 overall quality |
| quality_breakdown | JSONB | NULL | Dimension scores (length, coverage, etc.) |
| quality_suggestions | TEXT[] | NULL | Improvement suggestions |

**Validation**: `source` in ('manual', 'auto_generated'). `quality_score` in [0, 100] when set.

**Note**: `generated_with_ai` remains for backward compatibility; `source` distinguishes manual vs autonomous generation.

---

### autonomous_runs (new)

Audit trail for each autonomous pipeline execution. Supports monitoring and debugging.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Primary key |
| user_id | UUID | FK users(id), NOT NULL | User |
| started_at | TIMESTAMPTZ | DEFAULT NOW() | |
| completed_at | TIMESTAMPTZ | NULL | |
| status | VARCHAR(20) | NOT NULL | running, success, partial, failed |
| jobs_discovered | INTEGER | DEFAULT 0 | |
| jobs_qualified | INTEGER | DEFAULT 0 | |
| proposals_generated | INTEGER | DEFAULT 0 | |
| notifications_sent | INTEGER | DEFAULT 0 | |
| errors | JSONB | NULL | List of error messages |
| metadata | JSONB | NULL | Extra context |

**Indexes**: user_id, started_at DESC, status

---

## State Transitions

### Autonomy Level → Pipeline Behavior

| Level | Discovery | Qualification | Notify | Auto-Generate |
|-------|-----------|---------------|--------|---------------|
| assisted | Manual only | Manual | No | No |
| semi_autonomous | Scheduled | Yes | Yes (if enabled) | Yes (if enabled) |
| fully_autonomous | Scheduled | Yes | Yes | Yes |

### Job Qualification Flow

1. Job discovered → inserted/updated in `jobs`
2. Qualification runs → score computed, `user_job_qualifications` upserted
3. If score >= notification_threshold and notifications_enabled → send notification
4. If score >= auto_generate_threshold and auto_generate_enabled → create proposal with source='auto_generated'

---

## Key Entities (from Spec)

- **User Profile**: Extended with autonomy settings (keywords from `keywords` table, skills/budget from preferences or future columns)
- **Job/Opportunity**: Existing `jobs` table; qualification score in `user_job_qualifications`
- **Qualified Job**: Job with `user_job_qualifications` row where score >= user's threshold
- **Proposal Draft**: `proposals` with `source`, `quality_score`, `quality_suggestions`
- **Autonomous Run**: `autonomous_runs` row per pipeline execution
