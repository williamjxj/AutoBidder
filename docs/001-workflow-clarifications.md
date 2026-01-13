# Clarifications & Q/A: Workflow Optimization (001)

**Feature**: 001-smooth-workflow  
**Date**: January 12, 2026  
**Status**: Needs Review  
**Purpose**: Document unclear environment variables, configuration decisions, and questions requiring stakeholder input

---

## Overview

This document captures questions and clarifications needed for the Workflow Optimization feature that couldn't be determined from existing codebase or best practices. Stakeholders should review and provide answers.

---

## Section 1: Environment Variables

### 1.1 Backend Configuration (backend/.env)

| Variable | Current Value | Question | Options | Recommendation |
|----------|---------------|----------|---------|----------------|
| `SESSION_STATE_TTL_HOURS` | 24 (proposed) | How long should session state persist after last activity? | A) 24 hours<br>B) 7 days<br>C) 30 days<br>D) Indefinite | **A (24 hours)** - Balances cleanup with reasonable return window |
| `DRAFT_RETENTION_HOURS` | 24 (proposed) | How long should auto-saved drafts be retained? | A) 12 hours<br>B) 24 hours<br>C) 48 hours<br>D) 7 days | **B (24 hours)** - Per user choice in spec clarification |
| `MAX_DRAFT_SIZE_KB` | 1000 (proposed) | Maximum size for a single draft? | A) 500 KB<br>B) 1 MB (1000 KB)<br>C) 5 MB<br>D) 10 MB | **B (1 MB)** - Sufficient for typical proposals, prevents abuse |
| `ENABLE_WORKFLOW_ANALYTICS` | true (proposed) | Should we collect workflow performance analytics? | A) true<br>B) false | **A (true)** - Required to validate success criteria |

#### Questions:

**Q1.1**: Should `SESSION_STATE_TTL_HOURS` differ between development and production?
- **Context**: Dev environments may want longer retention for debugging
- **Proposed**: Dev = 168 hours (7 days), Prod = 24 hours
- **Impact**: Development database will accumulate more session states
- **Answer**: _[PENDING]_

**Q1.2**: Do we need `MAX_DRAFTS_PER_USER` limit?
- **Context**: Prevent single user from creating thousands of drafts
- **Proposed**: 50 drafts per user (across all entity types)
- **Impact**: Requires additional validation in draft API
- **Answer**: _[PENDING]_

**Q1.3**: Should analytics be sent to external service (e.g., Mixpanel, Amplitude)?
- **Context**: Currently planned for internal PostgreSQL table
- **Options**: 
  - A) PostgreSQL only (simple, contained)
  - B) PostgreSQL + Mixpanel (better analytics tools)
  - C) Mixpanel only (reduce database load)
- **Proposed**: A (PostgreSQL only) for MVP, B for post-launch
- **Answer**: _[PENDING]_

---

### 1.2 Frontend Configuration (frontend/.env.local)

| Variable | Current Value | Question | Options | Recommendation |
|----------|---------------|----------|---------|----------------|
| `NEXT_PUBLIC_BACKEND_API_URL` | http://localhost:8000 (dev) | What's the production backend URL? | _[NEEDS ANSWER]_ | Depends on deployment |
| `NEXT_PUBLIC_AUTO_SAVE_INTERVAL_MS` | 10000 (proposed) | How often should auto-save checkpoint run? | A) 5000 (5s)<br>B) 10000 (10s)<br>C) 30000 (30s) | **B (10s)** - Per spec FR-005 |
| `NEXT_PUBLIC_OFFLINE_SYNC_RETRY_MS` | 5000 (proposed) | Delay before retrying failed offline sync? | A) 2000 (2s)<br>B) 5000 (5s)<br>C) 10000 (10s) | **B (5s)** - Balance between responsiveness and server load |
| `NEXT_PUBLIC_VIRTUAL_SCROLL_THRESHOLD` | 100 (proposed) | When should virtual scrolling activate? | A) 50 items<br>B) 100 items<br>C) 200 items | **B (100 items)** - Per research decision |

#### Questions:

**Q1.4**: What is the production backend API URL?
- **Context**: Frontend needs to know where to send API requests in production
- **Options**:
  - A) https://api.auto-bidder.com
  - B) Same domain as frontend (e.g., https://app.auto-bidder.com/api via Next.js rewrites)
  - C) Supabase Edge Functions URL
- **Impact**: Affects CORS configuration, deployment strategy
- **Answer**: _[NEEDS ANSWER]_

**Q1.5**: Should auto-save interval be configurable per-user?
- **Context**: Power users might want faster saves, others might prefer less frequent
- **Proposed**: No (global setting), add user preference in future iteration
- **Impact**: Adds complexity (user settings table, UI)
- **Answer**: _[PENDING]_

**Q1.6**: Should we show "unsaved changes" warning on browser close?
- **Context**: Standard pattern to prevent accidental data loss
- **Proposed**: Yes, use `beforeunload` event when drafts have unsaved changes
- **Implementation**: 
  ```javascript
  window.addEventListener('beforeunload', (e) => {
    if (hasUnsavedChanges) {
      e.preventDefault();
      e.returnValue = '';
    }
  });
  ```
- **Answer**: _[PENDING]_

---

## Section 2: Production Environment Questions

### 2.1 Deployment Configuration

**Q2.1**: Where will the application be deployed?
- **Options**:
  - A) Vercel (Frontend) + Railway/Render (Backend) + Supabase (Database)
  - B) AWS (all components)
  - C) Self-hosted VPS
  - D) Other: _[SPECIFY]_
- **Impact**: Affects environment variable management, CI/CD setup
- **Answer**: _[NEEDS ANSWER]_

**Q2.2**: How should environment variables be managed in production?
- **Options**:
  - A) Platform environment variables (Vercel, Railway, etc.)
  - B) `.env.production` files (committed to private repo)
  - C) Secret management service (AWS Secrets Manager, Vault)
  - D) Other: _[SPECIFY]_
- **Proposed**: A for MVP (simplest)
- **Answer**: _[PENDING]_

**Q2.3**: Should frontend environment variables differ per deployment environment?
- **Context**: May want different settings for staging vs production
- **Environments**: Development, Staging, Production
- **Example Differences**:
  - Auto-save interval: Dev=10s, Staging=10s, Prod=10s (same)
  - Analytics enabled: Dev=false, Staging=true, Prod=true
  - Backend URL: Different for each environment
- **Answer**: _[NEEDS ANSWER]_

---

### 2.2 Supabase Configuration

**Q2.4**: Are Supabase environment variables already configured?
- **Required Variables**:
  - Backend: `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`
  - Frontend: `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- **Check**:
  ```bash
  # Backend
  grep -E "SUPABASE_(URL|SERVICE_KEY)" backend/.env
  
  # Frontend
  grep -E "NEXT_PUBLIC_SUPABASE_(URL|ANON_KEY)" frontend/.env.local
  ```
- **Status**: _[NEEDS VERIFICATION]_

**Q2.5**: Do we need separate Supabase projects for dev/staging/prod?
- **Context**: Best practice for data isolation
- **Proposed**: 
  - Dev: Local PostgreSQL (docker-compose)
  - Staging: Supabase project #1
  - Production: Supabase project #2
- **Impact**: Requires managing multiple project URLs/keys
- **Answer**: _[PENDING]_

---

## Section 3: Performance & Scaling

### 3.1 Database Performance

**Q3.1**: What are expected database volumes?
- **Session States**: 1 row per active user (estimate: 10-100 concurrent users)
- **Drafts**: 5-10 drafts per user average (estimate: 50-1000 total drafts)
- **Analytics**: 100-500 events per user per day (estimate: 1k-50k events/day)

**Questions**:
- Total expected user count (monthly active users)? _[NEEDS ANSWER]_
- Peak concurrent users? _[NEEDS ANSWER]_
- Analytics retention period (90 days proposed)? _[PENDING]_

**Q3.2**: Should we partition the `workflow_analytics` table?
- **Context**: High-volume analytics data may benefit from partitioning
- **Proposed**: Yes, partition by month if >100k rows expected per month
- **Implementation**: PostgreSQL table partitioning by `created_at`
- **Answer**: _[PENDING]_

**Q3.3**: Do we need read replicas for analytics queries?
- **Context**: Separate analytics reads from transactional writes
- **Proposed**: No for MVP, consider if analytics queries cause slowdown
- **Answer**: _[PENDING]_

---

### 3.2 API Rate Limiting

**Q3.4**: Should workflow APIs have different rate limits?
- **Context**: Current backend has `RATE_LIMIT_PER_MINUTE=10` in config
- **Proposed Limits**:
  - Session State: 60/minute (frequent updates expected)
  - Draft Save: 120/minute (auto-save every 10s = 6/min per user)
  - Offline Sync: 10/minute (occasional batches)
  - Analytics: 1000/minute (high volume, low cost)
- **Answer**: _[PENDING]_

**Q3.5**: Should rate limits differ between authenticated and anonymous users?
- **Context**: All workflow features require authentication
- **Proposed**: N/A (no anonymous access to workflow APIs)
- **Answer**: _[CONFIRMED]_

---

## Section 4: Security & Privacy

### 4.1 Data Privacy

**Q4.1**: Can draft data contain sensitive information?
- **Context**: Proposals might include budget, strategy, client info
- **Proposed**: Yes, treat all draft data as sensitive
- **Implications**:
  - Encrypt draft_data column? (PostgreSQL pgcrypto)
  - Access logs for draft access?
  - Data retention compliance (GDPR, CCPA)?
- **Answer**: _[NEEDS ANSWER]_

**Q4.2**: Should we implement draft encryption at rest?
- **Context**: Additional security layer for sensitive draft data
- **Options**:
  - A) No encryption (rely on Supabase/database security)
  - B) Encrypt draft_data JSONB column (PostgreSQL pgcrypto)
  - C) Encrypt at application layer (Python/TypeScript)
- **Proposed**: A for MVP (Supabase provides encryption at rest)
- **Answer**: _[PENDING]_

**Q4.3**: Should users be able to permanently delete all their workflow data?
- **Context**: GDPR "right to be forgotten" compliance
- **Proposed**: Yes, extend user deletion to cascade to:
  - `user_session_states` (already has ON DELETE CASCADE)
  - `draft_work` (already has ON DELETE CASCADE)
  - `workflow_analytics` (already has ON DELETE CASCADE)
- **Status**: Already handled by CASCADE, no action needed
- **Answer**: _[CONFIRMED]_

---

### 4.2 Authentication

**Q4.4**: Are there any special authentication requirements for workflow APIs?
- **Context**: Currently using Supabase JWT tokens
- **Questions**:
  - Should session tokens have shorter expiry for security? _[PENDING]_
  - Do we need refresh token rotation? _[PENDING]_
  - Should workflow APIs require additional MFA? _[PENDING]_
- **Proposed**: Use existing Supabase auth (no changes)
- **Answer**: _[PENDING]_

---

## Section 5: Feature Flags & Rollout

### 5.1 Feature Flags

**Q5.1**: Should workflow features be behind feature flags?
- **Context**: Allow gradual rollout, A/B testing, emergency disable
- **Proposed Feature Flags**:
  - `workflow.auto_save` - Enable/disable auto-save
  - `workflow.offline_mode` - Enable/disable offline queue
  - `workflow.keyboard_shortcuts` - Enable/disable shortcuts
  - `workflow.virtual_scroll` - Enable/disable virtual scrolling
  - `workflow.analytics` - Enable/disable analytics collection
- **Implementation**: 
  - Backend: Environment variables (simple)
  - Frontend: Environment variables or feature flag service (LaunchDarkly, Unleash)
- **Answer**: _[PENDING]_

**Q5.2**: Should different users see different features (A/B testing)?
- **Context**: Validate impact of workflow optimizations
- **Proposed**: Yes, for measuring SC-004 (30% task completion time reduction)
- **Implementation**: 
  - Control group: Existing workflow (no optimization features)
  - Test group: Full workflow optimization
  - Duration: 2-4 weeks
  - Metrics: Task completion time, user satisfaction, support tickets
- **Answer**: _[PENDING]_

---

## Section 6: Monitoring & Alerting

### 6.1 Error Monitoring

**Q6.1**: What error monitoring service should we use?
- **Options**:
  - A) Sentry (popular, good free tier)
  - B) Rollbar
  - C) LogRocket (includes session replay)
  - D) Built-in logging only
- **Proposed**: A (Sentry) for both backend and frontend
- **Answer**: _[NEEDS ANSWER]_

**Q6.2**: What errors should trigger alerts?
- **Proposed Critical Alerts**:
  - Auto-save failure rate >5%
  - Offline sync failure rate >10%
  - Page transition time >1000ms (p95)
  - Database connection errors
  - Draft data loss (conflict resolution failed)
- **Alert Destinations**: Email, Slack, PagerDuty?
- **Answer**: _[NEEDS ANSWER]_

---

### 6.2 Performance Monitoring

**Q6.3**: Should we use APM (Application Performance Monitoring)?
- **Context**: Track performance beyond basic analytics
- **Options**:
  - A) New Relic
  - B) Datadog
  - C) Built-in monitoring (Next.js Analytics, FastAPI metrics)
  - D) None (rely on workflow_analytics table)
- **Proposed**: C (built-in) for MVP, upgrade if needed
- **Answer**: _[PENDING]_

---

## Section 7: Testing & CI/CD

### 7.1 Testing Requirements

**Q7.1**: What is the minimum required test coverage?
- **Proposed**:
  - Backend: 80% coverage for workflow services
  - Frontend: 70% coverage for workflow hooks/components
  - E2E: Core user flows covered (navigation, auto-save, offline)
- **Answer**: _[PENDING]_

**Q7.2**: Should E2E tests run on every commit or only pre-merge?
- **Context**: E2E tests are slower, may impact CI speed
- **Proposed**: Unit tests on every commit, E2E on PR only
- **Answer**: _[PENDING]_

---

### 7.2 Deployment Strategy

**Q7.3**: What is the deployment strategy?
- **Options**:
  - A) Continuous Deployment (auto-deploy on merge to main)
  - B) Manual deployment (after QA approval)
  - C) Staged rollout (deploy to 10% → 50% → 100% of users)
- **Proposed**: C (staged rollout) for this feature (high risk, core UX impact)
- **Answer**: _[NEEDS ANSWER]_

**Q7.4**: Is there a rollback plan?
- **Context**: If feature causes issues, can we quickly disable/rollback?
- **Proposed Rollback Options**:
  1. Feature flags (instant disable)
  2. Revert deployment (5-10 minutes)
  3. Database migration rollback (if schema issues)
- **Answer**: _[PENDING]_

---

## Section 8: Documentation

### 8.1 User Documentation

**Q8.1**: Do we need end-user documentation for workflow features?
- **Context**: Most features are transparent (auto-save, state preservation)
- **Proposed Documentation**:
  - In-app tooltips for keyboard shortcuts (press `?` to see list)
  - Help article: "How Auto-Save Works"
  - Help article: "Working Offline with Auto-Bidder"
  - No separate user guide needed
- **Answer**: _[PENDING]_

---

## Summary of Pending Answers

| Priority | Question ID | Question | Blocking? |
|----------|-------------|----------|-----------|
| **HIGH** | Q1.4 | Production backend API URL | Yes (deployment) |
| **HIGH** | Q2.1 | Deployment platform (Vercel/AWS/etc.) | Yes (deployment) |
| **HIGH** | Q2.4 | Supabase variables configured? | Yes (development) |
| **HIGH** | Q6.1 | Error monitoring service | Yes (production readiness) |
| **MEDIUM** | Q1.1 | Different TTL for dev vs prod? | No (can use same) |
| **MEDIUM** | Q1.2 | Max drafts per user limit? | No (add later if needed) |
| **MEDIUM** | Q1.6 | Browser close warning? | No (nice to have) |
| **MEDIUM** | Q3.1 | Expected user volumes? | No (affects optimization priority) |
| **MEDIUM** | Q5.1 | Feature flags needed? | No (but recommended) |
| **MEDIUM** | Q7.3 | Deployment strategy? | No (affects rollout plan) |
| **LOW** | Q1.3 | External analytics service? | No (PostgreSQL sufficient) |
| **LOW** | Q1.5 | Per-user auto-save interval? | No (future iteration) |
| **LOW** | Q3.2 | Partition analytics table? | No (optimize if needed) |
| **LOW** | Q4.2 | Draft encryption? | No (Supabase provides) |
| **LOW** | Q5.2 | A/B testing? | No (nice to have for validation) |

---

## Action Items

### For Product/Business Team:
1. [ ] Answer Q1.4 - Production backend URL
2. [ ] Answer Q2.1 - Deployment platform decision
3. [ ] Answer Q3.1 - User volume estimates
4. [ ] Answer Q6.1 - Error monitoring service choice
5. [ ] Answer Q7.3 - Deployment strategy preference
6. [ ] Review and approve proposed environment variable values

### For DevOps/Infrastructure Team:
1. [ ] Verify Q2.4 - Supabase configuration exists
2. [ ] Answer Q2.2 - Environment variable management strategy
3. [ ] Answer Q2.3 - Different configs per environment
4. [ ] Answer Q2.5 - Separate Supabase projects needed
5. [ ] Answer Q6.2 - Alerting destinations setup

### For Development Team:
1. [ ] Review all proposed values in tables above
2. [ ] Implement feature flags if Q5.1 approved
3. [ ] Set up error monitoring once Q6.1 answered
4. [ ] Update this document with answers as they come in
5. [ ] Create tickets for any new requirements discovered

---

## Document Status

- **Created**: January 12, 2026
- **Last Updated**: January 12, 2026
- **Status**: 🟡 Awaiting Stakeholder Input
- **Blocking Issues**: 4 high-priority questions need answers before production deployment
- **Next Review**: After stakeholder responses received

---

## Notes

- This document should be updated as questions are answered
- Cross-reference with [plan.md](../specs/001-smooth-workflow/plan.md) for technical context
- Stakeholders can add new questions in "Section 9: Additional Questions" below

---

## Section 8: Draft Cleanup Scheduler Setup

**Status**: Implementation Required  
**Priority**: Required before production deployment

The draft cleanup endpoint (`POST /api/drafts/cleanup`) has been implemented and needs to be called by a scheduled job to automatically delete expired drafts (older than 24 hours by default).

### Scheduler Options:

#### Option 1: Docker-based Cron (Recommended for local dev)
Add a cron service to `docker-compose.yml`:
```yaml
cron:
  image: alpine:latest
  command: >
    sh -c "echo '0 2 * * * curl -X POST http://backend:8000/api/drafts/cleanup' | crontab - && crond -f"
  depends_on:
    - backend
```

#### Option 2: GitHub Actions (Recommended for production)
Create `.github/workflows/cleanup-drafts.yml`:
```yaml
name: Cleanup Expired Drafts
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC
jobs:
  cleanup:
    runs-on: ubuntu-latest
    steps:
      - name: Call cleanup endpoint
        run: curl -X POST ${{ secrets.API_URL }}/api/drafts/cleanup?retention_hours=24
```

#### Option 3: PostgreSQL pg_cron Extension
Install pg_cron extension and create scheduled job:
```sql
-- Enable extension
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- Schedule cleanup job
SELECT cron.schedule(
  'cleanup-expired-drafts',
  '0 2 * * *',
  $$DELETE FROM draft_work WHERE updated_at < NOW() - INTERVAL '24 hours'$$
);
```

#### Option 4: Supabase Edge Functions (If using Supabase hosting)
Create a scheduled edge function that calls the cleanup endpoint.

**Decision Required**: Which scheduler option should be used for production?

**Current Status**: Endpoint implemented, scheduler setup needed.

---

## Section 9: Additional Questions

_[Space for stakeholders to add new questions as they arise]_

---

**Document Maintainer**: Development Team  
**Stakeholder Contact**: _[TO BE FILLED]_
