# Data Model: Workflow Optimization

**Feature**: 001-smooth-workflow  
**Date**: January 12, 2026  
**Database**: PostgreSQL (Supabase)

## Overview

This document defines database schema additions for workflow optimization features. All tables follow existing patterns: UUID primary keys, RLS policies, timestamp tracking, and Supabase integration.

---

## Schema Additions

### Table: `user_session_states`

**Purpose**: Store current workflow state per user to enable seamless navigation and context preservation (FR-002, FR-011).

**Schema**:

```sql
CREATE TABLE user_session_states (
  -- Primary Key
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL UNIQUE,
  
  -- Session Context
  active_feature VARCHAR(50), -- 'projects' | 'proposals' | 'keywords' | 'analytics' | 'knowledge-base' | 'settings'
  entity_id UUID, -- ID of currently viewed entity (project_id, proposal_id, etc.)
  
  -- Navigation State
  context_data JSONB DEFAULT '{}'::jsonb, -- { filters, selections, scrollPosition, tabs }
  navigation_history JSONB DEFAULT '[]'::jsonb, -- Last 10 navigation entries
  
  -- Metadata
  last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  -- Constraints
  CONSTRAINT active_feature_check CHECK (
    active_feature IN ('projects', 'proposals', 'keywords', 'analytics', 'knowledge-base', 'settings', 'strategies', 'dashboard')
  )
);

-- Indexes
CREATE UNIQUE INDEX idx_session_states_user_id ON user_session_states(user_id);
CREATE INDEX idx_session_states_last_activity ON user_session_states(last_activity_at);

-- RLS Policies
ALTER TABLE user_session_states ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own session state"
  ON user_session_states FOR ALL
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

-- Updated Timestamp Trigger
CREATE TRIGGER update_session_states_updated_at
  BEFORE UPDATE ON user_session_states
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();
```

**Field Descriptions**:

| Field | Type | Purpose | Example Value |
|-------|------|---------|---------------|
| `user_id` | UUID | User identifier (unique) | `123e4567-e89b-12d3-a456-426614174000` |
| `active_feature` | VARCHAR(50) | Current feature/page | `'proposals'` |
| `entity_id` | UUID | Currently viewed entity | Project/Proposal ID |
| `context_data` | JSONB | Page-specific state | `{"filters": {"status": "active"}, "scrollY": 250}` |
| `navigation_history` | JSONB | Recent navigation | `[{"path": "/projects", "timestamp": "2026-01-12T10:00:00Z"}]` |
| `last_activity_at` | TIMESTAMP | Last state update | `2026-01-12 10:30:45+00` |

**Context Data Examples**:

```json
// Projects page
{
  "filters": {
    "status": "active",
    "search": "design"
  },
  "sort": "updated_at_desc",
  "scrollPosition": 450,
  "selectedProjectId": "abc-123"
}

// Proposals page
{
  "filters": {
    "status": ["draft", "submitted"]
  },
  "activeTab": "drafts",
  "expandedSections": ["description", "budget"]
}

// Analytics page
{
  "dateRange": {
    "start": "2026-01-01",
    "end": "2026-01-12"
  },
  "selectedMetrics": ["win_rate", "avg_bid"]
}
```

**Size Limits**:
- `context_data`: ~10KB typical, 50KB max
- `navigation_history`: Limited to 10 entries, ~5KB typical

---

### Table: `draft_work`

**Purpose**: Store auto-saved drafts with 24-hour retention for recovery (FR-005, FR-007, FR-012).

**Schema**:

```sql
CREATE TABLE draft_work (
  -- Primary Key
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  
  -- Entity Reference
  entity_type VARCHAR(50) NOT NULL, -- 'proposal' | 'project' | 'keyword' | 'knowledge_document'
  entity_id UUID, -- NULL for new entities not yet created
  
  -- Draft Data
  draft_data JSONB NOT NULL, -- Full entity data being edited
  draft_version INTEGER DEFAULT 1, -- Increment on each save (conflict detection)
  
  -- Auto-Save Metadata
  auto_save_count INTEGER DEFAULT 0, -- Number of auto-saves performed
  last_auto_save_at TIMESTAMP WITH TIME ZONE,
  
  -- Lifecycle
  is_recovered BOOLEAN DEFAULT false, -- User saw recovery prompt
  recovered_at TIMESTAMP WITH TIME ZONE,
  expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '24 hours'),
  
  -- Timestamps
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  -- Constraints
  CONSTRAINT entity_type_check CHECK (
    entity_type IN ('proposal', 'project', 'keyword', 'knowledge_document', 'strategy')
  ),
  CONSTRAINT draft_data_size_check CHECK (
    pg_column_size(draft_data) < 1048576  -- 1MB max
  )
);

-- Indexes
CREATE UNIQUE INDEX idx_draft_work_user_entity ON draft_work(user_id, entity_type, entity_id) 
  WHERE entity_id IS NOT NULL;
CREATE INDEX idx_draft_work_expires_at ON draft_work(expires_at);
CREATE INDEX idx_draft_work_user_id ON draft_work(user_id);
CREATE INDEX idx_draft_work_is_recovered ON draft_work(is_recovered) 
  WHERE is_recovered = false;

-- RLS Policies
ALTER TABLE draft_work ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own drafts"
  ON draft_work FOR ALL
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

-- Updated Timestamp Trigger
CREATE TRIGGER update_draft_work_updated_at
  BEFORE UPDATE ON draft_work
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();
```

**Field Descriptions**:

| Field | Type | Purpose | Example Value |
|-------|------|---------|---------------|
| `entity_type` | VARCHAR(50) | Type of entity being edited | `'proposal'` |
| `entity_id` | UUID | Existing entity ID (NULL for new) | `abc-123...` or `NULL` |
| `draft_data` | JSONB | Full draft content | `{"title": "Website Redesign", "description": "..."}` |
| `draft_version` | INTEGER | Version number for conflict detection | `5` |
| `auto_save_count` | INTEGER | Number of auto-saves | `12` |
| `expires_at` | TIMESTAMP | Auto-cleanup time | `NOW() + 24 hours` |

**Draft Data Examples**:

```json
// Proposal draft
{
  "project_id": "proj-123",
  "title": "Website Redesign Proposal",
  "description": "Comprehensive redesign...",
  "budget_range": {
    "min": 5000,
    "max": 8000
  },
  "timeline_weeks": 6,
  "key_deliverables": [
    "Wireframes",
    "High-fidelity mockups"
  ],
  "status": "draft"
}

// Keyword draft (for batch creation)
{
  "keywords": [
    {
      "keyword": "react developer",
      "description": "Frontend specialist",
      "match_type": "partial"
    }
  ]
}
```

**Cleanup Strategy**:
- Cron job runs daily to delete rows where `expires_at < NOW()`
- User can manually discard draft (DELETE)
- Draft deleted when entity officially saved

---

### Table: `workflow_analytics`

**Purpose**: Track workflow performance metrics to validate success criteria (SC-002, SC-004, SC-008).

**Schema**:

```sql
CREATE TABLE workflow_analytics (
  -- Primary Key
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  
  -- Event Data
  event_type VARCHAR(100) NOT NULL, -- 'navigation', 'auto_save', 'draft_recovery', 'offline_sync', etc.
  event_category VARCHAR(50), -- 'performance' | 'user_action' | 'error'
  
  -- Metrics
  duration_ms INTEGER, -- For timing events (navigation, save, etc.)
  success BOOLEAN, -- For operations that can fail
  error_message TEXT, -- If success = false
  
  -- Context
  metadata JSONB DEFAULT '{}'::jsonb, -- Event-specific data
  user_agent TEXT, -- Browser info
  
  -- Timestamp
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  -- Constraints
  CONSTRAINT event_category_check CHECK (
    event_category IN ('performance', 'user_action', 'error', 'recovery')
  )
);

-- Indexes
CREATE INDEX idx_workflow_analytics_user_id ON workflow_analytics(user_id);
CREATE INDEX idx_workflow_analytics_event_type ON workflow_analytics(event_type);
CREATE INDEX idx_workflow_analytics_created_at ON workflow_analytics(created_at);
CREATE INDEX idx_workflow_analytics_category ON workflow_analytics(event_category);

-- RLS Policies
ALTER TABLE workflow_analytics ENABLE ROW LEVEL SECURITY;

-- Users can only read their own analytics
CREATE POLICY "Users can read own analytics"
  ON workflow_analytics FOR SELECT
  USING (auth.uid() = user_id);

-- Service role can insert analytics
CREATE POLICY "Service can insert analytics"
  ON workflow_analytics FOR INSERT
  WITH CHECK (true);

-- Partition by month for performance (optional, for high volume)
-- CREATE TABLE workflow_analytics_2026_01 PARTITION OF workflow_analytics
--   FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
```

**Field Descriptions**:

| Field | Type | Purpose | Example Value |
|-------|------|---------|---------------|
| `event_type` | VARCHAR(100) | Specific event | `'page_transition'` |
| `event_category` | VARCHAR(50) | Event grouping | `'performance'` |
| `duration_ms` | INTEGER | Time taken | `450` |
| `success` | BOOLEAN | Operation result | `true` |
| `metadata` | JSONB | Additional context | `{"from": "/projects", "to": "/proposals"}` |

**Event Type Examples**:

| Event Type | Category | Purpose | Metadata Example |
|------------|----------|---------|------------------|
| `page_transition` | performance | Track navigation speed (SC-002) | `{"from": "/projects", "to": "/analytics", "method": "link"}` |
| `auto_save` | user_action | Track auto-save frequency | `{"entity_type": "proposal", "size_bytes": 5200}` |
| `draft_recovery` | recovery | Track recovery usage (SC-010) | `{"entity_type": "proposal", "age_hours": 2, "action": "recovered"}` |
| `offline_sync` | performance | Track sync performance | `{"queued_count": 5, "synced_count": 5, "conflicts": 0}` |
| `keyboard_shortcut` | user_action | Track shortcut usage | `{"shortcut": "Cmd+K", "feature": "search"}` |
| `error_boundary` | error | Track unexpected errors | `{"component": "ProposalForm", "error": "TypeError..."}` |

**Analytics Queries** (for validating success criteria):

```sql
-- SC-002: 95% of transitions under 500ms
SELECT 
  PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY duration_ms) as p95_duration
FROM workflow_analytics
WHERE event_type = 'page_transition'
  AND created_at > NOW() - INTERVAL '7 days';

-- SC-004: Average task completion time
SELECT 
  event_type,
  AVG(duration_ms) as avg_duration,
  STDDEV(duration_ms) as stddev_duration
FROM workflow_analytics
WHERE event_category = 'performance'
  AND created_at > NOW() - INTERVAL '30 days'
GROUP BY event_type;

-- SC-010: Draft recovery rate
SELECT 
  COUNT(CASE WHEN metadata->>'action' = 'recovered' THEN 1 END)::float /
  COUNT(*)::float * 100 as recovery_rate_pct
FROM workflow_analytics
WHERE event_type = 'draft_recovery'
  AND created_at > NOW() - INTERVAL '30 days';
```

**Data Retention**:
- Keep 90 days of analytics data
- Archive or delete older data via cron job
- Aggregate metrics to separate reporting table if needed

---

## Migration Script

**File**: `database/migrations/004_workflow_optimization.sql`

```sql
-- Migration 004: Workflow Optimization
-- Created: 2026-01-12
-- Description: Add tables for session state, draft management, and workflow analytics

-- Prerequisites: uuid-ossp extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Function for updated_at trigger (if not exists)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

---
--- TABLE: user_session_states
---
-- [Full schema from above]

---
--- TABLE: draft_work
---
-- [Full schema from above]

---
--- TABLE: workflow_analytics
---
-- [Full schema from above]

-- Initial data (optional)
-- [Insert any seed data if needed]

-- Grants (Supabase handles this via RLS, but for completeness)
GRANT ALL ON user_session_states TO authenticated;
GRANT ALL ON draft_work TO authenticated;
GRANT SELECT, INSERT ON workflow_analytics TO authenticated;

-- Comments for documentation
COMMENT ON TABLE user_session_states IS 'Stores user workflow state for context preservation';
COMMENT ON TABLE draft_work IS 'Auto-saved drafts with 24-hour retention';
COMMENT ON TABLE workflow_analytics IS 'Performance and usage analytics for workflow optimization';
```

---

## Data Model Diagram

```
┌─────────────────────────┐
│   auth.users (Supabase) │
│   ─────────────────────  │
│   - id (UUID PK)         │
│   - email                │
└───────┬─────────────────┘
        │
        │ (one-to-one)
        ├──────────────────────────────────┐
        │                                  │
        │                                  │
┌───────▼──────────────────┐   ┌──────────▼────────────────┐
│ user_session_states      │   │ draft_work                │
│ ─────────────────────────│   │ ──────────────────────────│
│ - id (UUID PK)           │   │ - id (UUID PK)            │
│ - user_id (UUID FK)      │   │ - user_id (UUID FK)       │
│ - active_feature         │   │ - entity_type             │
│ - entity_id              │   │ - entity_id               │
│ - context_data (JSONB)   │   │ - draft_data (JSONB)      │
│ - navigation_history     │   │ - draft_version           │
│ - last_activity_at       │   │ - expires_at              │
└──────────────────────────┘   └───────────────────────────┘
        │
        │ (one-to-many)
        │
┌───────▼──────────────────┐
│ workflow_analytics       │
│ ─────────────────────────│
│ - id (UUID PK)           │
│ - user_id (UUID FK)      │
│ - event_type             │
│ - duration_ms            │
│ - metadata (JSONB)       │
│ - created_at             │
└──────────────────────────┘
```

---

## TypeScript Type Definitions

**File**: `frontend/src/types/workflow.ts`

```typescript
// Session State
export interface SessionState {
  id: string;
  userId: string;
  activeFeature: 
    | 'projects' 
    | 'proposals' 
    | 'keywords' 
    | 'analytics' 
    | 'knowledge-base' 
    | 'settings'
    | 'strategies'
    | 'dashboard';
  entityId?: string | null;
  contextData: Record<string, any>;
  navigationHistory: NavigationEntry[];
  lastActivityAt: string;
  createdAt: string;
  updatedAt: string;
}

export interface NavigationEntry {
  path: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

// Draft Work
export interface DraftWork {
  id: string;
  userId: string;
  entityType: 'proposal' | 'project' | 'keyword' | 'knowledge_document' | 'strategy';
  entityId?: string | null;
  draftData: Record<string, any>;
  draftVersion: number;
  autoSaveCount: number;
  lastAutoSaveAt?: string | null;
  isRecovered: boolean;
  recoveredAt?: string | null;
  expiresAt: string;
  createdAt: string;
  updatedAt: string;
}

// Workflow Analytics
export interface WorkflowAnalyticsEvent {
  id?: string;
  userId?: string;
  eventType: string;
  eventCategory: 'performance' | 'user_action' | 'error' | 'recovery';
  durationMs?: number;
  success?: boolean;
  errorMessage?: string;
  metadata?: Record<string, any>;
  userAgent?: string;
  createdAt?: string;
}
```

**File**: `frontend/src/types/database.ts` (additions)

```typescript
export interface Database {
  public: {
    Tables: {
      // ... existing tables ...
      
      user_session_states: {
        Row: SessionState;
        Insert: Omit<SessionState, 'id' | 'createdAt' | 'updatedAt'>;
        Update: Partial<Omit<SessionState, 'id' | 'userId'>>;
      };
      
      draft_work: {
        Row: DraftWork;
        Insert: Omit<DraftWork, 'id' | 'draftVersion' | 'autoSaveCount' | 'isRecovered' | 'createdAt' | 'updatedAt'>;
        Update: Partial<Omit<DraftWork, 'id' | 'userId'>>;
      };
      
      workflow_analytics: {
        Row: WorkflowAnalyticsEvent;
        Insert: Omit<WorkflowAnalyticsEvent, 'id' | 'createdAt'>;
        Update: never; // Analytics are append-only
      };
    };
  };
}
```

---

## Validation & Constraints

### Size Limits

| Table | Column | Limit | Enforcement |
|-------|--------|-------|-------------|
| `user_session_states` | `context_data` | 50KB | Client-side warning |
| `draft_work` | `draft_data` | 1MB | CHECK constraint |
| `workflow_analytics` | `metadata` | 10KB | Client-side truncation |

### Retention Policies

| Table | Retention | Cleanup Method |
|-------|-----------|----------------|
| `user_session_states` | Indefinite | Manual delete or on user delete |
| `draft_work` | 24 hours | Cron job (DELETE WHERE expires_at < NOW()) |
| `workflow_analytics` | 90 days | Cron job (archive then delete) |

### Cron Jobs (Supabase pg_cron)

```sql
-- Daily cleanup of expired drafts (runs at 2 AM UTC)
SELECT cron.schedule(
  'cleanup-expired-drafts',
  '0 2 * * *',
  $$
    DELETE FROM draft_work 
    WHERE expires_at < NOW();
  $$
);

-- Weekly analytics cleanup (runs Sunday 3 AM UTC)
SELECT cron.schedule(
  'cleanup-old-analytics',
  '0 3 * * 0',
  $$
    DELETE FROM workflow_analytics 
    WHERE created_at < NOW() - INTERVAL '90 days';
  $$
);
```

---

## Data Model Status

- ✅ **Schema Defined**: All tables, indexes, RLS policies documented
- ✅ **TypeScript Types**: Frontend types defined
- ✅ **Migration Script**: Ready to apply
- ✅ **Validation**: Size limits and constraints specified
- ⏭️ **Next Step**: Create API contracts in `/contracts` directory
