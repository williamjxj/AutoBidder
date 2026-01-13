# Implementation Plan: Workflow Optimization

**Branch**: `001-smooth-workflow` | **Date**: January 12, 2026 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/001-smooth-workflow/spec.md`

## Summary

This feature optimizes the user workflow across the Auto-Bidder application by implementing:

1. **Seamless Navigation** - Sub-500ms transitions, preserved context, keyboard shortcuts
2. **Progress Feedback** - Real-time indicators, actionable errors, undo capability
3. **Contextual Information** - Inline access to related data without navigation
4. **State Preservation** - Auto-save every 10s, draft recovery, 24-hour retention

**Technical Approach**: Implement client-side state management using React Context + localStorage for session state, IndexedDB for offline queue, and React Query for server state caching. Backend adds session state API endpoints to Supabase database.

## Technical Context

**Language/Version**: 
- Frontend: TypeScript 5.3+ with Next.js 15.3+, React 19
- Backend: Python 3.12 with FastAPI

**Primary Dependencies**:
- Frontend: Next.js, React Query (@tanstack/react-query), Supabase SSR, Radix UI, TailwindCSS
- Backend: FastAPI, Supabase Python client, Pydantic, PostgreSQL

**Storage**: 
- Primary: Supabase PostgreSQL (user data, session state, drafts)
- Client: localStorage (session context), IndexedDB (offline queue)
- Vector: ChromaDB (existing RAG features)

**Testing**:
- Frontend: Jest + React Testing Library (to be added)
- Backend: pytest (existing)
- E2E: Playwright (to be added for workflow testing)

**Target Platform**: Web (Chrome, Firefox, Safari, Edge latest versions)

**Project Type**: Web application (Next.js frontend + FastAPI backend)

**Performance Goals**:
- Page transitions: <500ms (95th percentile)
- Auto-save latency: <100ms (perceived as instant)
- Offline sync: <2s for queued changes
- Virtual scroll rendering: 60fps with 1000+ items

**Constraints**:
- Must work with intermittent connectivity
- Single-session workflow (one active task across tabs)
- 24-hour draft retention limit
- Browser must support localStorage and online/offline events (graceful degradation for older browsers)

**Scale/Scope**:
- Expected users per instance: 10-100 concurrent
- Drafts per user: 5-10 concurrent
- Session state size: ~10-50KB per user
- Analytics events: 100-500 per user per session

## Constitution Check

*NOTE: Project constitution template is not yet populated. Skipping detailed gate validation.*

**Assumed Principles** (based on codebase analysis):
- ✅ **Type Safety**: TypeScript frontend, Python type hints with Pydantic
- ✅ **Testing**: pytest for backend, plan includes frontend testing setup
- ✅ **Database-First**: Using Supabase PostgreSQL with migrations
- ✅ **Modern Stack**: React 19, Next.js 15, FastAPI, Python 3.12

**Post-Design Re-Check**: Will verify after Phase 1 that data models follow existing patterns and API contracts align with FastAPI standards.

## Project Structure

### Documentation (this feature)

```text
specs/001-smooth-workflow/
├── plan.md              # This file
├── research.md          # Technology decisions and patterns (Phase 0)
├── data-model.md        # Database schema additions (Phase 1)
├── quickstart.md        # Developer setup guide (Phase 1)
├── contracts/           # API specifications (Phase 1)
│   ├── session-state-api.yaml
│   ├── draft-api.yaml
│   └── offline-sync-api.yaml
└── tasks.md             # Task breakdown (created by /speckit.tasks)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── config.py              # [MODIFY] Add session/draft config
│   ├── main.py                # [MODIFY] Add new routers
│   ├── models/                # [NEW] Add session_state.py, draft.py
│   ├── routers/               # [NEW] Add session.py, draft.py, sync.py
│   ├── services/              # [MODIFY] Extend supabase_client.py
│   │   ├── session_manager.py       # [NEW] Session state operations
│   │   ├── draft_manager.py         # [NEW] Draft CRUD + recovery
│   │   └── conflict_resolver.py     # [NEW] Last-write-wins logic
│   └── core/
│       └── middleware.py      # [NEW] Performance timing middleware
├── tests/
│   ├── unit/
│   │   ├── test_session_manager.py  # [NEW]
│   │   ├── test_draft_manager.py    # [NEW]
│   │   └── test_conflict_resolver.py # [NEW]
│   └── integration/
│       └── test_workflow_api.py     # [NEW] End-to-end workflow tests
└── requirements.txt           # [MODIFY] Add new dependencies if needed

frontend/
├── src/
│   ├── app/(dashboard)/       # [MODIFY] All feature pages
│   │   ├── layout.tsx         # [MODIFY] Add WorkflowProvider
│   │   ├── projects/          # [MODIFY] Add state preservation
│   │   ├── proposals/         # [MODIFY] Add auto-save
│   │   ├── keywords/          # [MODIFY] Add inline editing
│   │   └── analytics/         # [MODIFY] Add contextual actions
│   ├── components/
│   │   ├── workflow/          # [NEW] Workflow-specific components
│   │   │   ├── auto-save-indicator.tsx
│   │   │   ├── offline-banner.tsx
│   │   │   ├── progress-overlay.tsx
│   │   │   ├── undo-toast.tsx
│   │   │   ├── conflict-dialog.tsx
│   │   │   └── keyboard-shortcuts.tsx
│   │   ├── shared/
│   │   │   ├── app-sidebar.tsx      # [MODIFY] Add keyboard nav
│   │   │   └── top-header.tsx       # [MODIFY] Add offline indicator
│   │   └── ui/                # [EXISTING] Shadcn components
│   ├── lib/
│   │   ├── workflow/          # [NEW] Core workflow logic
│   │   │   ├── session-context.tsx  # React Context for session state
│   │   │   ├── draft-manager.ts     # Client-side draft operations
│   │   │   ├── offline-queue.ts     # IndexedDB queue for offline changes
│   │   │   ├── conflict-handler.ts  # Client-side conflict resolution
│   │   │   └── keyboard-handler.ts  # Global keyboard shortcuts
│   │   ├── api/
│   │   │   └── client.ts            # [MODIFY] Add workflow endpoints
│   │   └── hooks/             # [NEW] Workflow hooks
│   │       ├── useAutoSave.ts
│   │       ├── useOfflineSync.ts
│   │       ├── useSessionState.ts
│   │       ├── useUndo.ts
│   │       └── useKeyboardShortcuts.ts
│   └── types/
│       ├── workflow.ts        # [NEW] Workflow type definitions
│       └── database.ts        # [MODIFY] Add new table types
├── tests/                     # [NEW] Frontend tests
│   ├── unit/
│   │   ├── draft-manager.test.ts
│   │   ├── offline-queue.test.ts
│   │   └── hooks.test.ts
│   └── e2e/
│       ├── navigation.spec.ts
│       ├── auto-save.spec.ts
│       └── offline-mode.spec.ts
└── package.json               # [MODIFY] Add testing dependencies

database/
├── migrations/
│   └── 004_workflow_optimization.sql  # [NEW] Session + draft tables
└── seed/
    └── dev_workflow_data.sql          # [NEW] Test data for workflows

docs/
└── 001-workflow-clarifications.md     # [NEW] Environment variable Q/A
```

**Structure Decision**: Using existing web application structure with backend/frontend separation. Workflow features integrate into existing dashboard layout and extend API with new routers. Following established patterns: Supabase for data, FastAPI routers for API, React Context for client state, React Query for server state caching.

## Complexity Tracking

> **No violations detected.** This feature builds upon existing architecture without introducing new structural complexity. Following established patterns throughout.

---

## Phase 0: Research & Technology Decisions

See [research.md](./research.md) for detailed findings.

**Key Decisions**:

1. **Client State Management**: React Context API + localStorage
   - Rationale: Lightweight, built-in, sufficient for single-session workflow
   - Alternatives: Redux (too heavy), Zustand (unnecessary dependency)

2. **Offline Storage**: IndexedDB via idb library
   - Rationale: Supports structured data, good browser support, async API
   - Alternatives: localStorage (size limits), WebSQL (deprecated)

3. **Auto-Save Strategy**: Debounced onChange + periodic checkpoint
   - Rationale: Balance between data safety and server load
   - Alternatives: On every keystroke (excessive), manual only (defeats purpose)

4. **Virtual Scrolling**: react-window library
   - Rationale: Battle-tested, handles 1000+ items efficiently
   - Alternatives: react-virtualized (older), custom implementation (risky)

5. **Performance Monitoring**: Next.js built-in Web Vitals + custom timing middleware
   - Rationale: Zero-config for client, lightweight FastAPI middleware for server
   - Alternatives: External APM (premature), none (can't measure success criteria)

---

## Phase 1: Data Model & API Contracts

See [data-model.md](./data-model.md) for complete schemas.

### Database Schema Additions

**New Tables**:

1. **user_session_states** - Stores current workflow state per user
   - Fields: user_id, active_feature, context_data (JSONB), navigation_history, created_at, updated_at
   - Indexes: user_id (unique), updated_at

2. **draft_work** - Stores auto-saved drafts
   - Fields: id, user_id, entity_type, entity_id, draft_data (JSONB), expires_at, created_at, updated_at
   - Indexes: user_id + entity_type + entity_id (unique), expires_at

3. **workflow_analytics** - Tracks workflow performance metrics
   - Fields: id, user_id, event_type, duration_ms, metadata (JSONB), created_at
   - Indexes: user_id, event_type, created_at

### API Endpoints

See [contracts/](./contracts/) directory for OpenAPI specifications.

**New FastAPI Routers**:

1. **Session State API** (`/api/session/*`)
   - GET `/api/session/state` - Get current session state
   - PUT `/api/session/state` - Update session state
   - DELETE `/api/session/state` - Clear session state

2. **Draft API** (`/api/drafts/*`)
   - GET `/api/drafts` - List user's active drafts
   - GET `/api/drafts/{entity_type}/{entity_id}` - Get specific draft
   - PUT `/api/drafts/{entity_type}/{entity_id}` - Save draft
   - DELETE `/api/drafts/{entity_type}/{entity_id}` - Discard draft
   - POST `/api/drafts/cleanup` - Remove expired drafts (cron job)

3. **Offline Sync API** (`/api/sync/*`)
   - POST `/api/sync/batch` - Sync queued offline changes
   - GET `/api/sync/conflicts` - Get pending conflicts
   - POST `/api/sync/resolve` - Resolve conflict (overwrite or discard)

4. **Analytics API** (`/api/analytics/*`)
   - POST `/api/analytics/workflow-event` - Record workflow timing event

### Frontend API Client Updates

**New TypeScript API Functions** (in `lib/api/client.ts`):

```typescript
// Session State
async function getSessionState(): Promise<SessionState>
async function updateSessionState(state: Partial<SessionState>): Promise<void>

// Drafts
async function saveDraft(entityType: string, entityId: string, data: any): Promise<void>
async function getDraft(entityType: string, entityId: string): Promise<Draft | null>
async function discardDraft(entityType: string, entityId: string): Promise<void>

// Offline Sync
async function syncOfflineQueue(changes: OfflineChange[]): Promise<SyncResult>
async function resolveConflict(conflictId: string, action: 'overwrite' | 'discard'): Promise<void>

// Analytics
async function recordWorkflowEvent(eventType: string, duration: number, metadata?: any): Promise<void>
```

---

## Phase 2: Implementation Sequence

**NOTE**: Phase 2 task breakdown is created by `/speckit.tasks` command, not this plan.

**High-Level Implementation Order** (for context):

1. **Backend Foundation** (P1 - Week 1)
   - Database migrations
   - Session state API + service
   - Draft API + service
   - Conflict resolution logic

2. **Frontend Foundation** (P1 - Week 1)
   - Workflow context provider
   - Session state hooks
   - Draft manager + hooks
   - Offline queue infrastructure

3. **Navigation & Feedback** (P1 - Week 2)
   - Performance timing middleware
   - Loading indicators
   - Error handling improvements
   - Keyboard shortcuts

4. **Auto-Save & Recovery** (P2 - Week 2)
   - Auto-save implementation
   - Draft recovery UI
   - Conflict detection + resolution
   - Undo functionality

5. **Offline Support** (P2 - Week 3)
   - Offline detection
   - Queue management
   - Sync logic
   - Conflict handling UI

6. **Contextual Features** (P3 - Week 3)
   - Inline editing components
   - Related data display
   - Quick actions
   - Tooltips & help

7. **Large Dataset Optimization** (P3 - Week 4)
   - Virtual scrolling implementation
   - Pagination backend support
   - Performance testing
   - Optimization tuning

8. **Testing & Polish** (Week 4)
   - Unit tests
   - Integration tests
   - E2E workflow tests
   - Performance validation
   - Documentation

---

## Integration Points

### Backend ↔ Database
- **Supabase Client**: Existing `app/services/supabase_client.py` extended with session/draft operations
- **Database Migrations**: New `004_workflow_optimization.sql` adds tables with RLS policies
- **Configuration**: Add session/draft config to `app/config.py` (max draft size, retention period)

### Backend ↔ Frontend
- **API Communication**: Frontend uses existing `lib/api/client.ts` pattern with new workflow endpoints
- **Authentication**: Supabase JWT tokens passed in headers (existing pattern)
- **CORS**: Already configured in `backend/app/main.py` for localhost:3000
- **Error Format**: Follow existing FastAPI error response structure

### Frontend State Management
- **Server State**: React Query for caching API responses (existing pattern)
- **Session State**: New React Context provider wrapping dashboard layout
- **Local Storage**: Direct localStorage API for persistence
- **IndexedDB**: idb library wrapper for offline queue

### Frontend ↔ Browser APIs
- **Online/Offline Events**: `window.addEventListener('online/offline')`
- **localStorage**: For session state (max 5MB assumed)
- **IndexedDB**: For offline queue (quota API for capacity check)
- **Performance API**: `performance.mark()` / `performance.measure()` for timing
- **Keyboard Events**: `window.addEventListener('keydown')` with Cmd/Ctrl detection

---

## Environment Variables & Configuration

### Backend Environment Variables (backend/.env)

**Existing** (from config.py):
- ✅ `OPENAI_API_KEY` - OpenAI API key
- ✅ `SUPABASE_URL` - Supabase project URL
- ✅ `SUPABASE_SERVICE_KEY` - Supabase service role key
- ✅ `DATABASE_URL` - PostgreSQL connection string
- ✅ `CHROMA_PERSIST_DIR` - ChromaDB storage path
- ✅ `CORS_ORIGINS` - Allowed frontend origins
- ✅ `LOG_LEVEL` - Logging level
- ✅ `ENVIRONMENT` - deployment environment

**New** (to be added):
- `SESSION_STATE_TTL_HOURS` - Session state expiration (default: 24)
- `DRAFT_RETENTION_HOURS` - Draft auto-cleanup period (default: 24)
- `MAX_DRAFT_SIZE_KB` - Maximum draft size (default: 1000)
- `ENABLE_WORKFLOW_ANALYTICS` - Toggle analytics collection (default: true)

### Frontend Environment Variables (frontend/.env.local)

**Existing**:
- ✅ `NEXT_PUBLIC_SUPABASE_URL` - Supabase project URL
- ✅ `NEXT_PUBLIC_SUPABASE_ANON_KEY` - Supabase anon key

**New** (to be added):
- `NEXT_PUBLIC_BACKEND_API_URL` - Backend API base URL (default: http://localhost:8000)
- `NEXT_PUBLIC_AUTO_SAVE_INTERVAL_MS` - Auto-save frequency (default: 10000)
- `NEXT_PUBLIC_OFFLINE_SYNC_RETRY_MS` - Offline sync retry delay (default: 5000)
- `NEXT_PUBLIC_ENABLE_KEYBOARD_SHORTCUTS` - Toggle shortcuts (default: true)
- `NEXT_PUBLIC_VIRTUAL_SCROLL_THRESHOLD` - When to enable virtual scroll (default: 100)

### Docker Compose Updates (docker-compose.yml)

**Backend Service** - Add new environment variables:
```yaml
environment:
  # ... existing vars ...
  - SESSION_STATE_TTL_HOURS=24
  - DRAFT_RETENTION_HOURS=24
  - MAX_DRAFT_SIZE_KB=1000
  - ENABLE_WORKFLOW_ANALYTICS=true
```

**Frontend Service** (currently commented out) - Add when enabled:
```yaml
environment:
  # ... existing vars ...
  - NEXT_PUBLIC_BACKEND_API_URL=http://backend:8000
  - NEXT_PUBLIC_AUTO_SAVE_INTERVAL_MS=10000
  - NEXT_PUBLIC_OFFLINE_SYNC_RETRY_MS=5000
```

### Configuration Clarifications Needed

See [docs/001-workflow-clarifications.md](../../docs/001-workflow-clarifications.md) for:
- Questions about environment-specific configuration values
- Production vs development differences
- Scaling considerations for session/draft storage

---

## Performance Targets & Validation

**Success Criteria Mapping** (from spec.md):

1. **SC-002**: 95% of page transitions <500ms
   - **Measurement**: Custom React hook tracking navigation start/complete
   - **Validation**: E2E tests + production monitoring

2. **SC-003**: Zero data loss incidents
   - **Measurement**: Auto-save success rate + draft recovery usage
   - **Validation**: Integration tests + user feedback

3. **SC-004**: 30% reduction in task completion time
   - **Measurement**: Workflow analytics comparing before/after
   - **Validation**: A/B testing or historical comparison

4. **SC-008**: 100% progress feedback for operations >1s
   - **Measurement**: Audit all async operations for indicators
   - **Validation**: Manual QA + E2E tests

5. **SC-010**: 80% draft recovery completion rate
   - **Measurement**: Drafts recovered / drafts offered
   - **Validation**: Analytics tracking

**Performance Testing Plan**:
- Lighthouse CI for page transitions
- React DevTools Profiler for render performance
- Backend load testing with 100 concurrent users
- Offline queue stress test with 1000+ queued changes

---

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Browser storage quota exceeded | High | Implement quota checking, warn user, cleanup old drafts |
| IndexedDB not supported (older browsers) | Medium | Graceful degradation to localStorage with reduced offline capability |
| Race conditions in auto-save | High | Debouncing + optimistic locking with version numbers |
| Network flakiness causing repeated failed syncs | Medium | Exponential backoff + max retry limit |
| User has 20+ tabs open causing state sync issues | Low | Single-session model ensures tabs sync to same state |
| Large datasets (10k+ projects) slowing UI | Medium | Virtual scrolling + pagination enforced at 100+ items |
| Auto-save overwhelming server | Medium | Client-side debouncing (300ms) + rate limiting backend |

---

## Developer Quickstart

See [quickstart.md](./quickstart.md) for detailed setup instructions.

**Quick Summary**:

```bash
# 1. Database setup
docker-compose up -d postgres
cd database/migrations && psql -f 004_workflow_optimization.sql

# 2. Backend setup
cd backend
source venv/bin/activate
pip install -r requirements.txt
# Add new env vars to backend/.env
uvicorn app.main:app --reload

# 3. Frontend setup
cd frontend
npm install  # Installs new dependencies
# Add new env vars to frontend/.env.local
npm run dev

# 4. Run tests
cd backend && pytest tests/unit/test_session_manager.py
cd frontend && npm run test
```

---

## Next Steps

1. ✅ **Review this plan** - Ensure technical approach aligns with team preferences
2. ⏭️ **Run `/speckit.tasks`** - Break down implementation into specific developer tasks
3. ⏭️ **Review clarifications** - Answer questions in docs/001-workflow-clarifications.md
4. ⏭️ **Begin Phase 1** - Start with database migrations + backend API
5. ⏭️ **Iterate** - Implement in priority order (P1 → P2 → P3)

**Estimated Effort**: 3-4 weeks for single full-stack developer

**Priority**: P1 (High) - Directly impacts core user experience and workflow efficiency
