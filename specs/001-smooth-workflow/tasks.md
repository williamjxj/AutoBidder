# Tasks: Workflow Optimization

**Input**: Design documents from `/specs/001-smooth-workflow/`  
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/, research.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

**Tests**: Tests are optional and not included by default. Add test tasks if TDD approach is desired.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/app/` for source, `backend/tests/` for tests
- **Frontend**: `frontend/src/` for source, `frontend/tests/` for tests
- **Database**: `database/migrations/` for SQL migrations

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, environment configuration, and dependency setup

- [x] T001 Add new environment variables to backend/.env (SESSION_STATE_TTL_HOURS, DRAFT_RETENTION_HOURS, MAX_DRAFT_SIZE_KB, ENABLE_WORKFLOW_ANALYTICS)
- [x] T002 Add new environment variables to frontend/.env.local (NEXT_PUBLIC_BACKEND_API_URL, NEXT_PUBLIC_AUTO_SAVE_INTERVAL_MS, NEXT_PUBLIC_OFFLINE_SYNC_RETRY_MS, NEXT_PUBLIC_ENABLE_KEYBOARD_SHORTCUTS, NEXT_PUBLIC_VIRTUAL_SCROLL_THRESHOLD)
- [x] T003 [P] Install frontend dependencies: idb, react-window in frontend/package.json
- [x] T004 [P] Update docker-compose.yml with new backend environment variables
- [x] T005 [P] Create backend/app/models/ directory structure (session_state.py, draft.py will be added later)
- [x] T006 [P] Create backend/app/services/ directory for workflow services
- [x] T007 [P] Create backend/app/routers/ files (session.py, draft.py, sync.py will be added later)
- [x] T008 [P] Create frontend/src/lib/workflow/ directory structure
- [x] T009 [P] Create frontend/src/components/workflow/ directory
- [x] T010 [P] Create frontend/src/hooks/ directory for workflow hooks
- [x] T011 [P] Create frontend/src/types/workflow.ts for TypeScript type definitions

**Checkpoint**: Project structure ready for implementation

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database & Core Models

- [x] T012 Apply database migration database/migrations/004_workflow_optimization.sql to create user_session_states, draft_work, and workflow_analytics tables
- [x] T013 Verify migration success by querying new tables in PostgreSQL
- [x] T014 [P] Update frontend/src/types/database.ts with new table types (SessionState, DraftWork, WorkflowAnalyticsEvent)
- [x] T015 [P] Create complete TypeScript type definitions in frontend/src/types/workflow.ts (SessionState, NavigationEntry, DraftWork, OfflineChange, Conflict, etc.)

### Backend Core Infrastructure

- [x] T016 Update backend/app/config.py to add workflow-related settings (session_state_ttl_hours, draft_retention_hours, max_draft_size_kb, enable_workflow_analytics)
- [x] T017 [P] Create backend/app/core/middleware.py with performance timing middleware for tracking request duration
- [x] T018 [P] Update backend/app/services/supabase_client.py to extend with workflow table operations helper methods
- [x] T019 Update backend/app/main.py to include new routers (import session, draft, sync routers - will be created in user stories)

### Frontend Core Infrastructure

- [x] T020 [P] Create frontend/src/lib/api/client.ts workflow API functions (getSessionState, updateSessionState, saveDraft, getDraft, syncOfflineQueue, resolveConflict, recordWorkflowEvent)
- [x] T021 Create frontend/src/lib/workflow/session-context.tsx with React Context Provider for session state management
- [x] T022 [P] Create frontend/src/lib/workflow/storage-utils.ts with localStorage and IndexedDB helper functions
- [x] T023 Update frontend/src/app/(dashboard)/layout.tsx to wrap with WorkflowProvider from session-context

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Seamless Navigation Between Features (Priority: P1) 🎯 MVP

**Goal**: Enable fast (<500ms) navigation between features with preserved context, responsive transitions, and browser navigation support

**Independent Test**: Navigate between projects → analytics → proposals, use browser back button, verify filters/state preserved and transitions complete quickly with visual feedback

### Backend Implementation for US1

- [x] T024 [P] [US1] Create backend/app/models/session_state.py with SessionState Pydantic model matching database schema
- [x] T025 [P] [US1] Create backend/app/services/session_manager.py with SessionManager class (get_state, update_state, delete_state methods)
- [x] T026 [US1] Create backend/app/routers/session.py with FastAPI router implementing GET/PUT/DELETE /api/session/state endpoints per contracts/session-state-api.yaml
- [x] T027 [US1] Update backend/app/main.py to include session router with prefix="/api"
- [x] T028 [US1] Add error handling and validation to session router (400 for invalid data, 404 for not found, 413 for payload too large)

### Frontend Implementation for US1

- [x] T029 [P] [US1] Implement frontend/src/lib/workflow/session-context.tsx with complete SessionProvider including state management, localStorage persistence, and API sync
- [x] T030 [P] [US1] Create frontend/src/hooks/useSessionState.ts hook for components to access and update session state
- [x] T031 [P] [US1] Create frontend/src/hooks/useNavigationTiming.ts hook to track navigation performance using Performance API
- [x] T032 [P] [US1] Create frontend/src/components/workflow/progress-overlay.tsx component for loading states during navigation
- [x] T033 [US1] Update frontend/src/components/shared/app-sidebar.tsx to integrate with session context and preserve active state
- [x] T034 [US1] Create frontend/src/app/(dashboard)/projects/page.tsx to persist filters and scroll position using session context
- [x] T035 [US1] Create frontend/src/app/(dashboard)/proposals/page.tsx to persist state using session context
- [x] T036 [US1] Create frontend/src/app/(dashboard)/analytics/page.tsx to persist state using session context
- [x] T037 [US1] Implement context preservation on browser back/forward navigation in all dashboard pages

### Performance Tracking for US1

- [x] T038 [P] [US1] Create backend/app/models/analytics.py with WorkflowAnalyticsEvent Pydantic model
- [x] T039 [P] [US1] Create backend/app/routers/analytics.py with POST /api/analytics/workflow-event endpoint
- [x] T040 [US1] Update backend/app/main.py to include analytics router
- [x] T041 [US1] Implement frontend performance tracking in useNavigationTiming hook to send timing data to analytics API
- [x] T042 [US1] Add middleware timing to backend/app/core/middleware.py to track server-side response times

**Checkpoint**: At this point, User Story 1 should be fully functional - navigation is fast, context is preserved, performance is tracked

---

## Phase 4: User Story 4 - Workflow State Preservation (Priority: P2)

**Goal**: Automatically save user work every 10 seconds, recover drafts after interruptions, prevent data loss, maintain 24-hour retention

**Independent Test**: Start creating a proposal, wait 10s for auto-save, close browser, reopen, verify draft recovery prompt appears and data is restored

**Dependencies**: Requires US1 (session context) to be complete

### Backend Implementation for US4

- [x] T043 [P] [US4] Create backend/app/models/draft.py with Draft Pydantic model matching draft_work table schema
- [x] T044 [P] [US4] Create backend/app/services/draft_manager.py with DraftManager class (list_drafts, get_draft, save_draft, delete_draft, cleanup_expired methods)
- [x] T045 [P] [US4] Create backend/app/services/conflict_resolver.py with ConflictResolver class implementing last-write-wins logic with version checking
- [x] T046 [US4] Create backend/app/routers/draft.py with FastAPI router implementing all draft endpoints per contracts/draft-api.yaml (GET /api/drafts, GET/PUT/DELETE /api/drafts/{type}/{id}, POST /api/drafts/cleanup)
- [x] T047 [US4] Update backend/app/main.py to include draft router
- [x] T048 [US4] Add validation in draft router (1MB size limit, version conflict detection, 409 response on conflict)
- [x] T049 [US4] Set up cron job or scheduler for POST /api/drafts/cleanup to run daily cleanup of expired drafts

### Frontend Auto-Save Implementation for US4

- [x] T050 [P] [US4] Create frontend/src/lib/workflow/draft-manager.ts with DraftManager class (saveDraft, getDraft, deleteDraft, listDrafts methods)
- [x] T051 [P] [US4] Create frontend/src/hooks/useAutoSave.ts hook implementing debounced onChange (300ms) + 10-second periodic checkpoint logic
- [x] T052 [P] [US4] Create frontend/src/hooks/useDraftRecovery.ts hook to check for and offer recovery of drafts on page load
- [x] T053 [P] [US4] Create frontend/src/components/workflow/auto-save-indicator.tsx showing "Saving..." / "Saved" / "Failed" status
- [x] T054 [US4] Integrate useAutoSave hook into frontend/src/app/(dashboard)/proposals/new/page.tsx proposal creation form
- [x] T055 [US4] Integrate useDraftRecovery hook into frontend/src/app/(dashboard)/proposals/new/page.tsx to show recovery banner on load
- [x] T056 [US4] Add auto-save indicator to proposal form UI showing save status

### Conflict Handling for US4

- [x] T057 [P] [US4] Create frontend/src/lib/workflow/conflict-handler.ts with conflict detection and resolution logic
- [x] T058 [P] [US4] Create frontend/src/components/workflow/conflict-dialog.tsx showing conflict resolution options (overwrite or discard)
- [x] T059 [US4] Integrate conflict detection into draft save flow in draft-manager.ts to detect 409 responses
- [x] T060 [US4] Show conflict dialog when conflict detected, allow user to choose resolution action
- [x] T061 [US4] Test conflict scenario: open same proposal in two tabs, edit both, save, verify conflict warning appears (Testing task - implementation complete)

**Checkpoint**: At this point, User Story 4 should be fully functional - auto-save works, drafts recover, conflicts are handled gracefully

---

## Phase 5: User Story 2 - Progress Visibility and Feedback (Priority: P2)

**Goal**: Provide clear visual feedback for all operations, show progress indicators for long operations, display actionable error messages, enable undo within 5 seconds

**Independent Test**: Submit a proposal, see progress indicator; trigger an error, see clear actionable message; complete action, see success message with undo option

**Dependencies**: Can build on US1 and US4 infrastructure

### Progress Indicators for US2

- [x] T062 [P] [US2] Update frontend/src/components/workflow/progress-overlay.tsx to support estimated completion time display
- [x] T063 [P] [US2] Create frontend/src/hooks/useProgressTracking.ts hook to track and display progress for long-running operations
- [ ] T064 [US2] Add progress overlay to proposal submission flow in frontend/src/app/(dashboard)/proposals/[id]/page.tsx
- [ ] T065 [US2] Add progress overlay to project loading in frontend/src/app/(dashboard)/projects/page.tsx
- [ ] T066 [US2] Add loading skeletons to all dashboard pages for initial data loads

### Error Handling for US2

- [x] T067 [P] [US2] Create frontend/src/lib/errors/error-formatter.ts to format backend errors into actionable user messages
- [x] T068 [P] [US2] Create frontend/src/components/workflow/error-toast.tsx component for displaying errors with "what went wrong", "why it matters", and "how to fix" sections
- [x] T069 [US2] Update frontend/src/lib/api/client.ts to catch errors and format them using error-formatter before showing toast
- [x] T070 [US2] Update backend error responses in all routers to include actionable detail field per API contracts
- [x] T071 [US2] Test error scenarios: network failure, validation error, server error - verify all show actionable messages

### Success Confirmations & Undo for US2

- [x] T072 [P] [US2] Create frontend/src/hooks/useUndo.ts hook implementing undo functionality with 5-second window
- [x] T073 [P] [US2] Create frontend/src/components/workflow/undo-toast.tsx showing success message with undo button
- [ ] T074 [US2] Integrate undo hook into proposal save action in frontend/src/app/(dashboard)/proposals/[id]/page.tsx
- [ ] T075 [US2] Integrate undo hook into project update actions in frontend/src/app/(dashboard)/projects/[id]/page.tsx
- [ ] T076 [US2] Implement undo logic to revert last change and restore previous state
- [ ] T077 [US2] Test undo functionality: save proposal, click undo within 5s, verify reverted; wait >5s, verify undo option gone

### Background Operations for US2

- [x] T078 [P] [US2] Create frontend/src/lib/workflow/background-tasks.ts queue manager for background operations
- [ ] T079 [US2] Update long-running operations (e.g., bulk imports) to run in background using background-tasks queue
- [ ] T080 [US2] Add notification when background operation completes while user is on different page
- [ ] T081 [US2] Allow user to continue working on other pages while background operation runs

**Checkpoint**: At this point, User Story 2 should be fully functional - all operations have clear feedback, errors are actionable, undo works

---

## Phase 6: User Story 3 - Contextual Information Access (Priority: P3)

**Goal**: Display relevant information and actions inline without requiring navigation, enable inline editing from analytics, show related entities on entity pages

**Independent Test**: View analytics, click edit on underperforming keyword, edit inline; view project, see related proposals summary with quick actions

**Dependencies**: Builds on US1, US2, US4 infrastructure

### Inline Editing from Analytics for US3

- [ ] T082 [P] [US3] Create frontend/src/components/workflow/inline-edit-keyword.tsx component for editing keywords directly from analytics view
- [ ] T083 [US3] Update frontend/src/app/(dashboard)/analytics/page.tsx to integrate inline edit component for keywords
- [ ] T084 [US3] Add API call to update keyword from inline edit component without navigation
- [ ] T085 [US3] Show success toast after inline edit, update analytics view to reflect changes

### Contextual Knowledge Base Suggestions for US3

- [ ] T086 [P] [US3] Create frontend/src/lib/workflow/knowledge-suggester.ts to fetch relevant knowledge base articles based on project context
- [ ] T087 [P] [US3] Create frontend/src/components/workflow/knowledge-suggestions.tsx component displaying suggested articles inline
- [ ] T088 [US3] Integrate knowledge suggestions into frontend/src/app/(dashboard)/proposals/new/page.tsx proposal creation form
- [ ] T089 [US3] Add "Insert template" action to knowledge suggestions for quick content insertion

### Related Entities Display for US3

- [ ] T090 [P] [US3] Create frontend/src/components/workflow/related-proposals.tsx component showing recent proposals for a project with quick actions
- [ ] T091 [US3] Integrate related proposals component into frontend/src/app/(dashboard)/projects/[id]/page.tsx project detail page
- [ ] T092 [US3] Add quick actions to related proposals: "View", "Clone", "Edit"
- [ ] T093 [US3] Fetch related proposals data using React Query with caching

### Tooltips & Contextual Help for US3

- [ ] T094 [P] [US3] Create frontend/src/components/workflow/contextual-tooltip.tsx reusable tooltip component
- [ ] T095 [US3] Add tooltips to complex form fields across all dashboard forms (proposals, projects, keywords)
- [ ] T096 [US3] Add inline help text that appears on focus for fields requiring explanation
- [ ] T097 [US3] Create help overlay (press `?` key) showing keyboard shortcuts and tips

**Checkpoint**: At this point, User Story 3 should be fully functional - contextual information is accessible inline, no unnecessary navigation required

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Advanced features, optimizations, and final polish that affect multiple user stories

### Offline Support

- [ ] T098 [P] Create frontend/src/lib/workflow/offline-queue.ts with IndexedDB queue implementation for offline changes using idb library
- [ ] T099 [P] Create frontend/src/hooks/useOfflineSync.ts hook implementing batch sync with exponential backoff on reconnection
- [ ] T100 [P] Create frontend/src/components/workflow/offline-banner.tsx showing offline status with "Changes will sync when reconnected" message
- [ ] T101 Create backend/app/routers/sync.py with FastAPI router implementing POST /api/sync/batch, GET /api/sync/conflicts, POST /api/sync/resolve per contracts/offline-sync-api.yaml
- [ ] T102 Update backend/app/main.py to include sync router
- [ ] T103 Add online/offline event listeners to frontend/src/lib/workflow/offline-queue.ts to trigger sync on reconnection
- [ ] T104 Integrate offline queue into all data-modifying operations (create, update, delete)
- [ ] T105 Test offline scenario: go offline, make changes, go online, verify auto-sync with conflict resolution if needed

### Virtual Scrolling for Large Datasets

- [ ] T106 [P] Create frontend/src/components/workflow/virtual-list.tsx wrapper component using react-window library
- [ ] T107 Update frontend/src/app/(dashboard)/projects/page.tsx to use virtual-list when project count exceeds NEXT_PUBLIC_VIRTUAL_SCROLL_THRESHOLD
- [ ] T108 Update frontend/src/app/(dashboard)/proposals/page.tsx to use virtual scrolling for large proposal lists
- [ ] T109 Add pagination API support in backend if not already present for datasets >1000 items
- [ ] T110 Test performance with 1000+ items: verify 60fps scrolling and <500ms initial render

### Keyboard Shortcuts

- [ ] T111 [P] Create frontend/src/lib/workflow/keyboard-handler.ts implementing global keyboard shortcut handler with Cmd/Ctrl detection
- [ ] T112 [P] Create frontend/src/hooks/useKeyboardShortcuts.ts hook to register and use keyboard shortcuts
- [ ] T113 Integrate keyboard shortcuts into frontend/src/app/(dashboard)/layout.tsx: Cmd/Ctrl+N (new proposal), Cmd/Ctrl+K (search), Cmd/Ctrl+S (save)
- [ ] T114 Create keyboard shortcuts help overlay (press `?`) showing all available shortcuts
- [ ] T115 Test shortcuts across different browsers and operating systems (Mac vs Windows/Linux)

### Browser Compatibility & Graceful Degradation

- [ ] T116 [P] Create frontend/src/lib/workflow/browser-support.ts with feature detection functions (localStorage, IndexedDB, Performance API, online/offline events)
- [ ] T117 Implement graceful degradation logic: show one-time warning banner if localStorage or IndexedDB unavailable
- [ ] T118 Disable auto-save features if localStorage unavailable, require manual saves instead
- [ ] T119 Disable offline queue if IndexedDB unavailable, show "Online required" warning
- [ ] T120 Test in older browsers (Safari 14, Firefox ESR) to verify graceful degradation works

### Navigation Blocking During Critical Operations

- [ ] T121 [P] Create frontend/src/lib/workflow/navigation-guard.ts to block navigation during critical operations
- [ ] T122 Implement beforeunload event handler to show "Operation in progress, are you sure?" dialog
- [ ] T123 Add navigation guard to critical operations like bid submission, payment processing
- [ ] T124 Test navigation blocking: start critical operation, try to navigate away, verify confirmation dialog appears

### Documentation & Final Testing

- [ ] T125 [P] Update frontend/README.md with workflow optimization features and usage examples
- [ ] T126 [P] Update backend/README.md with new API endpoints and configuration
- [ ] T127 [P] Verify all items in specs/001-smooth-workflow/quickstart.md work correctly
- [ ] T128 [P] Create user documentation for keyboard shortcuts and workflow features in docs/ directory
- [ ] T129 Run complete end-to-end test of all 4 user stories to verify independent functionality
- [ ] T130 Performance validation: measure and verify SC-002 (95% of transitions <500ms using workflow_analytics table)
- [ ] T131 Data loss validation: verify SC-003 (zero data loss incidents through auto-save testing)
- [ ] T132 Draft recovery validation: verify SC-010 (80%+ recovery rate through analytics)
- [ ] T133 Code cleanup: remove console.logs, add missing TypeScript types, fix linter warnings
- [ ] T134 Security review: verify RLS policies work, test unauthorized access attempts
- [ ] T135 Create migration rollback script in case issues arise in production

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - **BLOCKS all user stories**
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion
- **User Story 4 (Phase 4)**: Depends on User Story 1 (needs session context)
- **User Story 2 (Phase 5)**: Depends on Foundational phase completion (can run parallel with US1 if resourced)
- **User Story 3 (Phase 6)**: Depends on Foundational phase completion (can run parallel with other stories)
- **Polish (Phase 7)**: Depends on desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories - **MVP CANDIDATE**
- **User Story 4 (P2)**: Depends on US1 session context - Should complete before US2/US3 for best UX
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Benefits from US1/US4 but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Benefits from US1/US2/US4 but independently testable

### Within Each User Story

- Backend models before services
- Services before API routers
- API routers before frontend integration
- Frontend hooks before components
- Core functionality before integration
- Story complete before moving to next priority

### Parallel Opportunities

**Setup Phase**: T003, T004, T005, T006, T007, T008, T009, T010, T011 can all run in parallel

**Foundational Phase**: 
- T014, T015 can run in parallel (frontend types)
- T017, T018 can run in parallel (backend middleware and services)
- T020, T022 can run in parallel (frontend utilities)

**User Story 1**:
- T024, T025 can run in parallel (backend models and services)
- T029, T030, T031, T032 can run in parallel (frontend hooks and components)
- T038, T039 can run in parallel (analytics models and routers)

**User Story 4**:
- T043, T044, T045 can run in parallel (backend models and services)
- T050, T051, T052, T053 can run in parallel (frontend draft management)
- T057, T058 can run in parallel (conflict handling)

**User Story 2**:
- T062, T063 can run in parallel (progress indicators)
- T067, T068 can run in parallel (error handling)
- T072, T073 can run in parallel (undo functionality)
- T078 can run in parallel (background tasks)

**User Story 3**:
- T082, T086, T090, T094 can all run in parallel (different components)

**Polish Phase**:
- T098, T099, T100 can run in parallel (offline support components)
- T106, T111, T116 can run in parallel (virtual scrolling, keyboard, browser support)
- T125, T126, T128 can run in parallel (documentation)

**Once Foundational is complete**: US1, US2, US3 can be developed in parallel by different team members (with note that US4 depends on US1)

---

## Parallel Example: User Story 1

```bash
# Launch all parallelizable backend tasks for US1:
Task T024: "Create backend/app/models/session_state.py"
Task T025: "Create backend/app/services/session_manager.py"
Task T038: "Create backend/app/models/analytics.py"
Task T039: "Create backend/app/routers/analytics.py"

# Launch all parallelizable frontend tasks for US1:
Task T029: "Implement frontend/src/lib/workflow/session-context.tsx"
Task T030: "Create frontend/src/hooks/useSessionState.ts"
Task T031: "Create frontend/src/hooks/useNavigationTiming.ts"
Task T032: "Create frontend/src/components/workflow/progress-overlay.tsx"
```

---

## Parallel Example: User Story 4

```bash
# Launch all parallelizable backend tasks for US4:
Task T043: "Create backend/app/models/draft.py"
Task T044: "Create backend/app/services/draft_manager.py"
Task T045: "Create backend/app/services/conflict_resolver.py"

# Launch all parallelizable frontend tasks for US4:
Task T050: "Create frontend/src/lib/workflow/draft-manager.ts"
Task T051: "Create frontend/src/hooks/useAutoSave.ts"
Task T052: "Create frontend/src/hooks/useDraftRecovery.ts"
Task T053: "Create frontend/src/components/workflow/auto-save-indicator.tsx"
Task T057: "Create frontend/src/lib/workflow/conflict-handler.ts"
Task T058: "Create frontend/src/components/workflow/conflict-dialog.tsx"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 4 Only)

1. Complete Phase 1: Setup (T001-T011)
2. Complete Phase 2: Foundational (T012-T023) - **CRITICAL - blocks all stories**
3. Complete Phase 3: User Story 1 - Seamless Navigation (T024-T042)
4. Complete Phase 4: User Story 4 - State Preservation (T043-T061)
5. **STOP and VALIDATE**: Test US1 + US4 independently together (navigation + auto-save MVP)
6. Deploy/demo if ready

**MVP Delivers**: Fast navigation with preserved context + auto-save with draft recovery = Core workflow improvement

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (T001-T023)
2. Add User Story 1 → Test independently → **Deploy/Demo** (T024-T042)
3. Add User Story 4 → Test independently → **Deploy/Demo** (T043-T061) - Now have MVP!
4. Add User Story 2 → Test independently → **Deploy/Demo** (T062-T081)
5. Add User Story 3 → Test independently → **Deploy/Demo** (T082-T097)
6. Add Polish features as needed → **Deploy/Demo** (T098-T135)
7. Each increment adds value without breaking previous functionality

### Parallel Team Strategy

With multiple developers (assuming 2-3 developers):

1. **Week 1**: All developers complete Setup + Foundational together (T001-T023)
2. **Week 1-2**: Once Foundational is done:
   - Developer A: User Story 1 (T024-T042)
   - Developer B: Can start User Story 2 (T062-T081) in parallel
3. **Week 2**: 
   - Developer A: After US1 complete, starts User Story 4 (T043-T061)
   - Developer B: Continues User Story 2
   - Developer C: Can start User Story 3 (T082-T097) in parallel
4. **Week 3-4**: 
   - All developers: Polish tasks (T098-T135) in parallel
   - Focus on highest-impact polish features first (offline support, keyboard shortcuts)

---

## Task Summary

**Total Tasks**: 135

**Tasks by Phase**:
- Phase 1 (Setup): 11 tasks
- Phase 2 (Foundational): 12 tasks (BLOCKING)
- Phase 3 (User Story 1 - P1): 19 tasks 🎯 MVP Component
- Phase 4 (User Story 4 - P2): 19 tasks 🎯 MVP Component
- Phase 5 (User Story 2 - P2): 20 tasks
- Phase 6 (User Story 3 - P3): 16 tasks
- Phase 7 (Polish): 38 tasks

**Parallelizable Tasks**: 58 tasks marked with [P] can run in parallel with other tasks

**Independent Test Criteria**:
- **US1**: Navigate projects → analytics → proposals, use back button, verify context preserved
- **US4**: Create proposal, wait 10s, close browser, reopen, verify draft recovery
- **US2**: Submit action, see progress; trigger error, see message; complete action, undo within 5s
- **US3**: Edit keyword from analytics inline; view project, see related proposals

**Suggested MVP Scope**: Phase 1 + Phase 2 + Phase 3 (US1) + Phase 4 (US4) = 61 tasks for core workflow optimization

**Estimated Timeline**:
- Single developer: 3-4 weeks for full feature
- Single developer (MVP only): 1.5-2 weeks
- 2 developers: 2-3 weeks for full feature
- 3 developers: 1.5-2 weeks for full feature

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [US1/US2/US3/US4] labels map tasks to specific user stories for traceability
- Each user story should be independently completable and testable
- Stop at any checkpoint to validate story independently
- Tests are optional - add test tasks (contract tests, integration tests, unit tests) if TDD approach desired
- Commit after each task or logical group of related tasks
- Refer to specs/001-smooth-workflow/ for detailed specifications, API contracts, and data models
- Use specs/001-smooth-workflow/quickstart.md for development setup and troubleshooting
- Validate against success criteria in spec.md after each user story completion
