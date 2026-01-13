/**
 * Workflow Optimization Type Definitions
 * 
 * Type definitions for session state management, draft management,
 * offline synchronization, and workflow analytics.
 */

// Session State Types
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

export interface SessionStateUpdate {
  activeFeature?: SessionState['activeFeature'];
  entityId?: string | null;
  contextData?: Record<string, any>;
  navigationEntry?: NavigationEntry;
}

// Draft Work Types
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

export interface DraftSaveRequest {
  draftData: Record<string, any>;
  expectedVersion?: number | null;
}

// Offline Sync Types
export interface OfflineChange {
  id: string;
  operation: 'create' | 'update' | 'delete';
  entityType: 'proposal' | 'project' | 'keyword' | 'knowledge_document' | 'strategy';
  entityId?: string | null;
  data?: Record<string, any>;
  timestamp: string;
  version?: number | null;
}

export interface SyncBatchResponse {
  synced: Array<{
    id: string;
    status: 'success';
    entityId?: string | null;
  }>;
  conflicts: Conflict[];
  failed: Array<{
    id: string;
    error: string;
    detail: string;
  }>;
  summary: {
    total: number;
    synced: number;
    conflicts: number;
    failed: number;
  };
}

// Conflict Types
export interface Conflict {
  id: string;
  entityType: 'proposal' | 'project' | 'keyword' | 'knowledge_document' | 'strategy';
  entityId: string;
  conflictType: 'version_mismatch' | 'concurrent_edit';
  clientData: Record<string, any>;
  serverData: Record<string, any>;
  clientVersion?: number | null;
  serverVersion: number;
  createdAt: string;
}

export interface ConflictResolution {
  conflictId: string;
  action: 'overwrite' | 'discard';
  resolvedData?: Record<string, any>;
}

// Workflow Analytics Types
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

// Browser Support Detection
export interface BrowserFeatures {
  localStorage: boolean;
  indexedDB: boolean;
  onlineEvents: boolean;
  performanceAPI: boolean;
}

export interface BrowserSupportStatus {
  supported: boolean;
  missing: string[];
  partial: boolean;
}

// Auto-Save Status
export interface AutoSaveStatus {
  status: 'idle' | 'saving' | 'saved' | 'error';
  lastSaved?: Date;
  error?: string;
}

// Navigation Timing
export interface NavigationTiming {
  path: string;
  startTime: number;
  endTime: number;
  duration: number;
}

// Undo Action
export interface UndoAction {
  id: string;
  action: string;
  timestamp: Date;
  data: Record<string, any>;
  canUndo: boolean;
}
