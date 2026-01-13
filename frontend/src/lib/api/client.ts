/**
 * API Client - HTTP Request Helper
 * Handles API requests with authentication headers and error handling
 */

import { createClient } from '@/lib/supabase/client'
import { errorFormatter } from '@/lib/errors/error-formatter'

interface RequestOptions extends RequestInit {
  body?: any
}

class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string = '/api') {
    this.baseUrl = baseUrl
  }

  private async getAuthHeaders(): Promise<HeadersInit> {
    const supabase = createClient()
    const {
      data: { session },
    } = await supabase.auth.getSession()

    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    }

    if (session?.access_token) {
      headers['Authorization'] = `Bearer ${session.access_token}`
    }

    return headers
  }

  private async request<T>(
    endpoint: string,
    options: RequestOptions = {}
  ): Promise<{ data: T | null; error: string | null }> {
    try {
      const headers = await this.getAuthHeaders()

      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        ...options,
        headers: {
          ...headers,
          ...options.headers,
        },
        body: options.body ? JSON.stringify(options.body) : undefined,
      })

      const data = await response.json()

      if (!response.ok) {
        // Create enhanced error object with response details
        const enhancedError = {
          status: response.status,
          response: { data, status: response.status },
          message: data.error || data.detail || `Request failed with status ${response.status}`,
          detail: data.detail,
        }

        // Format error for user-friendly display
        const formattedError = errorFormatter.format(enhancedError)

        return {
          data: null,
          error: formattedError.whatWentWrong,
        }
      }

      return { data, error: null }
    } catch (error) {
      // Format network/unexpected errors
      const formattedError = errorFormatter.format(error)
      
      return {
        data: null,
        error: formattedError.whatWentWrong,
      }
    }
  }

  async get<T>(endpoint: string, options?: RequestOptions) {
    return this.request<T>(endpoint, { ...options, method: 'GET' })
  }

  async post<T>(endpoint: string, body?: any, options?: RequestOptions) {
    return this.request<T>(endpoint, { ...options, method: 'POST', body })
  }

  async patch<T>(endpoint: string, body?: any, options?: RequestOptions) {
    return this.request<T>(endpoint, { ...options, method: 'PATCH', body })
  }

  async put<T>(endpoint: string, body?: any, options?: RequestOptions) {
    return this.request<T>(endpoint, { ...options, method: 'PUT', body })
  }

  async delete<T>(endpoint: string, options?: RequestOptions) {
    return this.request<T>(endpoint, { ...options, method: 'DELETE' })
  }

  /**
   * Get formatted error for display in toast/dialog
   */
  getFormattedError(error: any) {
    return errorFormatter.format(error)
  }
}

export const apiClient = new ApiClient()

// Workflow Optimization API Functions

import type {
  SessionState,
  SessionStateUpdate,
  DraftWork,
  DraftSaveRequest,
  OfflineChange,
  SyncBatchResponse,
  ConflictResolution,
  WorkflowAnalyticsEvent,
} from '@/types/workflow'

/**
 * Session State API
 */
export async function getSessionState(): Promise<SessionState | null> {
  const backend = process.env.NEXT_PUBLIC_BACKEND_API_URL || 'http://localhost:8000'
  const { data } = await apiClient.get<SessionState>(`${backend}/api/session/state`)
  return data
}

export async function updateSessionState(
  state: SessionStateUpdate
): Promise<SessionState | null> {
  const backend = process.env.NEXT_PUBLIC_BACKEND_API_URL || 'http://localhost:8000'
  const { data } = await apiClient.put<SessionState>(
    `${backend}/api/session/state`,
    state
  )
  return data
}

export async function deleteSessionState(): Promise<void> {
  const backend = process.env.NEXT_PUBLIC_BACKEND_API_URL || 'http://localhost:8000'
  await apiClient.delete(`${backend}/api/session/state`)
}

/**
 * Draft API
 */
export async function listDrafts(): Promise<DraftWork[]> {
  const backend = process.env.NEXT_PUBLIC_BACKEND_API_URL || 'http://localhost:8000'
  const { data } = await apiClient.get<{ drafts: DraftWork[] }>(
    `${backend}/api/drafts`
  )
  return data?.drafts || []
}

export async function getDraft(
  entityType: string,
  entityId: string
): Promise<DraftWork | null> {
  const backend = process.env.NEXT_PUBLIC_BACKEND_API_URL || 'http://localhost:8000'
  const { data } = await apiClient.get<DraftWork>(
    `${backend}/api/drafts/${entityType}/${entityId}`
  )
  return data
}

export async function saveDraft(
  entityType: string,
  entityId: string,
  draftRequest: DraftSaveRequest
): Promise<DraftWork | null> {
  const backend = process.env.NEXT_PUBLIC_BACKEND_API_URL || 'http://localhost:8000'
  const { data } = await apiClient.put<DraftWork>(
    `${backend}/api/drafts/${entityType}/${entityId}`,
    draftRequest
  )
  return data
}

export async function discardDraft(
  entityType: string,
  entityId: string
): Promise<void> {
  const backend = process.env.NEXT_PUBLIC_BACKEND_API_URL || 'http://localhost:8000'
  await apiClient.delete(`${backend}/api/drafts/${entityType}/${entityId}`)
}

/**
 * Offline Sync API
 */
export async function syncOfflineQueue(
  changes: OfflineChange[]
): Promise<SyncBatchResponse | null> {
  const backend = process.env.NEXT_PUBLIC_BACKEND_API_URL || 'http://localhost:8000'
  const { data } = await apiClient.post<SyncBatchResponse>(
    `${backend}/api/sync/batch`,
    { changes }
  )
  return data
}

export async function resolveConflict(
  resolution: ConflictResolution
): Promise<void> {
  const backend = process.env.NEXT_PUBLIC_BACKEND_API_URL || 'http://localhost:8000'
  await apiClient.post(`${backend}/api/sync/resolve`, resolution)
}

/**
 * Analytics API
 */
export async function recordWorkflowEvent(
  event: WorkflowAnalyticsEvent
): Promise<void> {
  const backend = process.env.NEXT_PUBLIC_BACKEND_API_URL || 'http://localhost:8000'
  await apiClient.post(`${backend}/api/analytics/workflow-event`, event)
}
