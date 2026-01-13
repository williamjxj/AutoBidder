# Research: Workflow Optimization Technology Decisions

**Feature**: 001-smooth-workflow  
**Date**: January 12, 2026  
**Status**: Completed

## Overview

This document captures technology research and architectural decisions for the Workflow Optimization feature. Each decision includes rationale, alternatives considered, and supporting evidence.

---

## 1. Client-Side State Management

### Decision: React Context API + localStorage

**Rationale**:
- React Context is built into React 19 (no additional dependencies)
- Sufficient for single-session workflow model (FR-011)
- localStorage provides 5-10MB storage, adequate for session state (~50KB)
- Aligns with Next.js 15 App Router patterns
- Team already familiar with Context API

**Alternatives Considered**:

| Alternative | Pros | Cons | Why Rejected |
|-------------|------|------|--------------|
| **Redux** | Powerful DevTools, mature ecosystem | 3 extra dependencies, boilerplate overhead | Over-engineered for single-session state |
| **Zustand** | Lightweight, simple API | Another dependency (7KB) | Context API sufficient for our needs |
| **Jotai** | Atomic state model, TypeScript-first | Learning curve, atomic model overkill | Simpler solution available |
| **Recoil** | Facebook-backed, atoms pattern | Meta framework (8KB), less mature | Context API meets requirements |

**Supporting Evidence**:
- React Context performance: Handles 10-20 re-renders/sec without issues
- localStorage sync operations: <1ms on modern browsers
- Next.js documentation recommends Context for cross-component state

**Implementation Notes**:
- Use `useContext` + `useReducer` for predictable state updates
- Memoize context value to prevent unnecessary re-renders
- Sync to localStorage on state changes (debounced)

---

## 2. Offline Storage & Queue Management

### Decision: IndexedDB via `idb` library

**Rationale**:
- IndexedDB provides structured storage (vs localStorage key-value)
- No size limit (quota API ~50-100MB typical)
- Async API (non-blocking)
- `idb` library provides Promise wrapper (3KB gzipped)
- Good browser support (95%+ of target browsers)

**Alternatives Considered**:

| Alternative | Pros | Cons | Why Rejected |
|-------------|------|------|--------------|
| **localStorage** | Simple API, synchronous | 5-10MB limit, blocking, key-value only | Size limits block offline queue scaling |
| **WebSQL** | SQL interface | Deprecated, removed from browsers | Not viable |
| **Cache API** | Service Worker integration | Complex for structured data, designed for HTTP cache | Wrong abstraction for app data |
| **Custom Service Worker** | Full control | High complexity, separate deployment | Premature optimization |

**Supporting Evidence**:
- IndexedDB quota API typically allocates 50MB+ on desktop browsers
- `idb` library battle-tested (3M+ weekly npm downloads)
- Offline queue expected to hold 10-50 changes (~50-500KB)

**Implementation Notes**:
- Use `idb` library for Promise-based API
- Create object stores: `offline_queue`, `drafts_cache`
- Implement periodic cleanup (delete synced items)
- Handle quota exceeded with user warning

**Graceful Degradation**:
- Detect IndexedDB support on mount
- Fall back to localStorage with warning
- Disable offline queue features if neither available

---

## 3. Auto-Save Strategy

### Decision: Debounced onChange + 10-second periodic checkpoint

**Rationale**:
- Debounced onChange (300ms): Captures user intent without overwhelming server
- 10-second checkpoint: Safety net for long typing sessions (FR-005)
- Optimistic UI: Show "saved" immediately, retry on failure
- Balances data safety (SC-003: zero data loss) with server load

**Alternatives Considered**:

| Alternative | Pros | Cons | Why Rejected |
|-------------|------|------|--------------|
| **Every keystroke** | Maximum safety | 10-100x server load, poor UX (constant saving indicators) | Excessive, violates performance goals |
| **Manual save only** | Zero server load, user control | Data loss risk (violates SC-003) | Defeats auto-save purpose |
| **On blur only** | Minimal server calls | Lost work if browser crashes mid-edit | Insufficient safety |
| **WebSocket streaming** | Real-time sync | Complex infrastructure, overkill | Over-engineered |

**Supporting Evidence**:
- Google Docs auto-saves every 500ms (we're conservative at 10s)
- Notion uses 300ms debounce + periodic save
- Linear uses similar pattern: debounce + checkpoint

**Implementation Notes**:
```typescript
// Debounced onChange
const debouncedSave = useMemo(
  () => debounce((data) => saveDraft(data), 300),
  []
);

// Periodic checkpoint
useEffect(() => {
  const interval = setInterval(() => {
    if (hasUnsavedChanges) saveDraft(currentData);
  }, 10000);
  return () => clearInterval(interval);
}, [hasUnsavedChanges, currentData]);
```

**Error Handling**:
- Retry with exponential backoff (1s, 2s, 4s)
- Show persistent warning if 3 retries fail
- Queue for offline sync if network unavailable

---

## 4. Virtual Scrolling for Large Datasets

### Decision: `react-window` library

**Rationale**:
- Battle-tested library (9M+ weekly npm downloads)
- Handles 1000+ items at 60fps (FR-017, SC-002)
- Lightweight (6KB gzipped)
- TypeScript support
- Simple API, easy to integrate with existing components

**Alternatives Considered**:

| Alternative | Pros | Cons | Why Rejected |
|-------------|------|------|--------------|
| **react-virtualized** | Feature-rich, mature | Larger (30KB), older API, less maintained | Older, heavier alternative |
| **@tanstack/react-virtual** | Modern, lightweight (3KB) | Newer, less proven, different API | Less mature ecosystem |
| **Custom implementation** | Full control, minimal size | High risk, complex edge cases | Not worth the risk |
| **Server pagination only** | Simple frontend | Poor UX (page loads), doesn't hit 60fps | Doesn't meet SC-002 |

**Supporting Evidence**:
- react-window benchmarks: 10K items at 60fps on mid-range devices
- Used by Airbnb, Slack, and other major apps
- Handles variable height items (needed for project cards)

**Implementation Notes**:
```typescript
import { FixedSizeList } from 'react-window';

<FixedSizeList
  height={600}
  itemCount={items.length}
  itemSize={80}
  width="100%"
>
  {({ index, style }) => (
    <div style={style}>{items[index]}</div>
  )}
</FixedSizeList>
```

**Activation Threshold**:
- Enable virtual scrolling when itemCount > 100 (configurable)
- Show pagination for 1000+ items (backend limit)

---

## 5. Performance Monitoring

### Decision: Next.js Web Vitals + Custom Timing Middleware

**Rationale**:
- Next.js provides built-in Web Vitals reporting (zero-config)
- Custom timing middleware captures server-side duration
- Performance API (browser) for client-side timing
- Lightweight, no external dependencies for basic monitoring
- Sufficient to validate SC-002 (95% < 500ms)

**Alternatives Considered**:

| Alternative | Pros | Cons | Why Rejected |
|-------------|------|------|--------------|
| **Sentry Performance** | Full APM, traces | Cost, complexity, overkill | Premature for MVP |
| **New Relic** | Enterprise features | High cost, heavy agent | Over-engineered |
| **Datadog RUM** | Real user monitoring | Expensive, requires setup | Not needed yet |
| **Custom analytics service** | Full control | Build/maintain infrastructure | Not core value |
| **No monitoring** | Zero effort | Can't validate success criteria | Unacceptable |

**Supporting Evidence**:
- Next.js Web Vitals sufficient for most startups pre-Series A
- Performance API has 98% browser support
- Can upgrade to full APM later if needed

**Implementation Notes**:

**Frontend** (Next.js):
```typescript
// app/layout.tsx
export function reportWebVitals(metric: NextWebVitalsMetric) {
  if (metric.name === 'TTFB' || metric.name === 'FCP') {
    recordWorkflowEvent(metric.name, metric.value);
  }
}
```

**Backend** (FastAPI middleware):
```python
# app/core/middleware.py
@app.middleware("http")
async def timing_middleware(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start_time) * 1000
    response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"
    return response
```

**Custom Timing Hooks**:
```typescript
// Track navigation timing
const useNavigationTiming = () => {
  useEffect(() => {
    const start = performance.now();
    return () => {
      const duration = performance.now() - start;
      recordWorkflowEvent('navigation', duration);
    };
  }, [pathname]);
};
```

---

## 6. Conflict Resolution Strategy

### Decision: Last-Write-Wins with User Notification

**Rationale**:
- Simplest to implement (no complex merge logic)
- Aligns with single-session model (FR-011)
- User is notified and can choose action (FR-013)
- Industry standard for document editors (Google Docs, Notion)

**Alternatives Considered**:

| Alternative | Pros | Cons | Why Rejected |
|-------------|------|------|--------------|
| **First-write-wins (locking)** | Prevents conflicts | Poor UX (locked out), complex distributed locking | Too restrictive |
| **Automatic merge** | Seamless UX | Complex logic, risk of bad merges | High complexity, low value |
| **Manual merge UI** | User control | Complex UI, poor UX for simple conflicts | Over-engineered |
| **Version history** | Can recover old versions | Requires additional storage, complex UI | Future enhancement |

**Implementation Notes**:
- Store `updated_at` timestamp with every draft
- On save, check if `updated_at` > local version
- If conflict detected, show dialog:
  - "This [proposal/project] was modified in another tab"
  - Options: "Use my changes" (overwrite) | "Discard my changes"
  - Optionally show diff (future enhancement)

**Edge Cases**:
- Multiple tabs: Single-session state ensures tabs see same draft
- Network delay: Timestamp comparison handles delayed saves
- Offline changes: Queue includes timestamp, resolved on sync

---

## 7. Keyboard Shortcuts Implementation

### Decision: Global window event listener with Cmd/Ctrl detection

**Rationale**:
- Simple, works across all pages
- Standard pattern for web apps
- FR-010 requires only 3 shortcuts (Create, Search, Save)
- Lightweight, no library needed

**Alternatives Considered**:

| Alternative | Pros | Cons | Why Rejected |
|-------------|------|------|--------------|
| **react-hotkeys-hook** | Declarative API, per-component | Extra dependency (8KB), overkill for 3 shortcuts | Over-engineered |
| **mousetrap** | Feature-rich | Extra dependency (10KB), dated API | Unnecessary |
| **Custom hook per component** | Component-scoped | Event listener per component (performance) | Inefficient |

**Implementation Notes**:
```typescript
// lib/workflow/keyboard-handler.ts
export function useKeyboardShortcuts() {
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      const isMac = navigator.platform.includes('Mac');
      const modifier = isMac ? e.metaKey : e.ctrlKey;
      
      if (modifier && e.key === 'n') {
        e.preventDefault();
        router.push('/dashboard/proposals/new');
      }
      if (modifier && e.key === 'k') {
        e.preventDefault();
        openSearchModal();
      }
      if (modifier && e.key === 's') {
        e.preventDefault();
        triggerSave();
      }
    };
    
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [router]);
}
```

**Accessibility**:
- Show keyboard shortcuts in help overlay (? key)
- Respect `prefers-reduced-motion` for animations

---

## 8. Browser Feature Detection & Graceful Degradation

### Decision: Feature detection on mount + one-time notification banner

**Rationale**:
- FR-016 requires graceful degradation
- Most users have modern browsers (Assumption #1)
- One-time notification prevents annoyance
- Core features still work without auto-save/offline

**Detection Strategy**:
```typescript
// lib/workflow/browser-support.ts
export function detectBrowserFeatures() {
  return {
    localStorage: typeof localStorage !== 'undefined',
    indexedDB: typeof indexedDB !== 'undefined',
    onlineEvents: 'onLine' in navigator,
    performanceAPI: typeof performance !== 'undefined',
  };
}

export function checkRequiredFeatures() {
  const features = detectBrowserFeatures();
  const missing = [];
  
  if (!features.localStorage) missing.push('localStorage');
  if (!features.indexedDB) missing.push('offline support');
  
  return {
    supported: missing.length === 0,
    missing,
    partial: features.localStorage && !features.indexedDB,
  };
}
```

**Fallback Matrix**:

| Feature | Requires | Fallback If Missing |
|---------|----------|---------------------|
| Auto-save | localStorage | Manual save only, show warning |
| Offline queue | IndexedDB | Disabled, show "online required" |
| Session state | localStorage | Session-only (no persistence) |
| Performance tracking | Performance API | Disabled silently |
| Network detection | Navigator.onLine | Assume always online |

**User Notification**:
```typescript
// Show once per session
if (!checkRequiredFeatures().supported) {
  showBanner({
    type: 'warning',
    message: 'Your browser has limited support. Auto-save and offline features are disabled.',
    dismissable: true,
    persist: false,
  });
}
```

---

## 9. Offline Queue Sync Strategy

### Decision: Batch sync on reconnection + exponential backoff

**Rationale**:
- Batch reduces server load (vs individual requests)
- Exponential backoff prevents thundering herd
- FR-015 requires automatic sync on reconnection
- Handles intermittent connectivity gracefully

**Sync Logic**:
```typescript
// lib/workflow/offline-queue.ts
async function syncOfflineQueue() {
  const navigator.onLine) return;
  
  const queue = await getOfflineQueue();
  if (queue.length === 0) return;
  
  try {
    const result = await api.syncBatch(queue);
    
    // Handle successful syncs
    await removeFromQueue(result.synced);
    
    // Handle conflicts
    if (result.conflicts.length > 0) {
      showConflictDialog(result.conflicts);
    }
    
    // Handle failures - retry with backoff
    if (result.failed.length > 0) {
      await scheduleRetry(result.failed);
    }
  } catch (error) {
    // Network error - retry in 5s, 10s, 20s, ...
    await scheduleRetry(queue, calculateBackoff());
  }
}

function calculateBackoff(attempt: number = 1): number {
  return Math.min(5000 * Math.pow(2, attempt - 1), 60000); // Max 60s
}
```

**Event Listeners**:
```typescript
// Sync on reconnection
window.addEventListener('online', () => {
  showToast('Back online. Syncing changes...');
  syncOfflineQueue();
});

// Warn on disconnection
window.addEventListener('offline', () => {
  showOfflineBanner('You\'re offline. Changes will sync when reconnected.');
});
```

---

## 10. Testing Strategy

### Decision: Jest + React Testing Library + Playwright

**Rationale**:
- Jest: Standard for React testing, fast, built into Next.js
- React Testing Library: User-centric testing, recommended by React team
- Playwright: Cross-browser E2E, modern API, fast
- Covers unit, integration, and E2E requirements

**Test Coverage Goals**:
- Unit tests: 80%+ for critical logic (draft manager, offline queue, hooks)
- Integration tests: All API endpoints, service layer
- E2E tests: Core user flows (navigation, auto-save, offline/online)

**Testing Tools**:

| Layer | Tool | Purpose |
|-------|------|---------|
| Frontend Unit | Jest + RTL | Component logic, hooks, utilities |
| Frontend E2E | Playwright | User workflows, cross-browser |
| Backend Unit | pytest | Service layer, business logic |
| Backend Integration | pytest + TestClient | API endpoints, database |
| Performance | Lighthouse CI | Page load, transitions |

**Key Test Scenarios**:
1. Auto-save triggers after 10 seconds
2. Draft recovery after browser crash
3. Offline changes queue and sync
4. Conflict resolution dialog appears
5. Virtual scrolling renders 1000+ items smoothly
6. Keyboard shortcuts work across pages
7. Network reconnection triggers sync

---

## Summary of Dependencies

### New Frontend Dependencies

```json
{
  "idb": "^8.0.0",              // IndexedDB wrapper
  "react-window": "^1.8.10",    // Virtual scrolling
  "@testing-library/react": "^14.1.2",  // Testing
  "@testing-library/jest-dom": "^6.1.5", // Test matchers
  "@playwright/test": "^1.40.0" // E2E testing
}
```

### New Backend Dependencies

```txt
# None required - using existing FastAPI, Supabase, pytest
```

### Dev Dependencies

```json
{
  "jest": "^29.7.0",
  "jest-environment-jsdom": "^29.7.0",
  "lighthouse": "^11.4.0"
}
```

---

## Open Questions & Future Enhancements

### Deferred to Future Iterations

1. **Full version history**: Track all draft versions, not just latest
   - Rationale: Not in MVP scope, adds complexity
   - Future value: User can recover any previous version

2. **Real-time collaboration**: Multiple users editing same entity
   - Rationale: Single-user workflow in MVP (FR-011)
   - Future value: Team collaboration features

3. **Advanced conflict resolution**: Visual diff, three-way merge
   - Rationale: Last-write-wins sufficient for MVP
   - Future value: Better UX for complex conflicts

4. **Offline-first architecture**: Service worker, full PWA
   - Rationale: Offline queue sufficient for intermittent connectivity
   - Future value: True offline app, installable

5. **Advanced analytics**: Session replay, funnel analysis
   - Rationale: Basic timing sufficient to validate SC-002
   - Future value: Deeper insights into user behavior

### Requires Clarification (see docs/001-workflow-clarifications.md)

1. Production environment variable values
2. Scaling limits for session storage
3. Analytics data retention policy

---

**Research Status**: ✅ Complete  
**Next Step**: Proceed to Phase 1 - Data Model & API Contracts
