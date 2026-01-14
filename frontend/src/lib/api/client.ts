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

  constructor(baseUrl: string = '') {
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

      const trimmedEndpoint = endpoint.trim()
      if (!trimmedEndpoint) {
        throw new Error('API endpoint cannot be empty')
      }

      // Determine the final URL
      let finalUrl: string

      if (/^(https?:)?\/\//i.test(trimmedEndpoint)) {
        // It's an absolute URL, use it directly
        finalUrl = trimmedEndpoint
      } else {
        // It's a relative URL, resolve against the backend
        const backend = getBackendUrl()

        // Ensure backend doesn't have trailing slash and path doesn't have leading slash
        const cleanBackend = backend.replace(/\/+$/, '')
        const cleanPath = trimmedEndpoint.replace(/^\/+/, '')

        finalUrl = `${cleanBackend}/${cleanPath}`
      }

      // Final validation to prevent malformed URLs like /apihttp:/...
      if (!finalUrl.startsWith('http://') && !finalUrl.startsWith('https://')) {
        // If it starts with /api but isn't absolute, it might have been incorrectly prefixed
        if (finalUrl.startsWith('/api')) {
          const backend = getBackendUrl()
          finalUrl = `${backend.replace(/\/+$/, '')}/${finalUrl.replace(/^\/+/, '')}`
        } else {
          throw new Error(`Invalid API URL: ${finalUrl}. URL must be absolute.`)
        }
      }

      // Log the request in development
      if (process.env.NODE_ENV === 'development') {
        console.log(`[ApiClient] ${options.method || 'GET'} ${finalUrl}`)
      }

      const response = await fetch(finalUrl, {
        ...options,
        headers: {
          ...headers,
          ...options.headers,
        },
        body: options.body ? JSON.stringify(options.body) : undefined,
      })

      // Handle non-JSON responses (e.g., 404 from Next.js)
      let data: any
      const contentType = response.headers.get('content-type')
      if (contentType && contentType.includes('application/json')) {
        data = await response.json()
      } else {
        // For non-JSON responses (like 404), create a simple error object
        data = {
          error: `Request failed with status ${response.status}`,
          status: response.status,
        }
      }

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
 * Get backend API URL from environment
 * Returns a properly formatted absolute URL
 */
function getBackendUrl(): string {
  const url = process.env.NEXT_PUBLIC_BACKEND_API_URL || 'http://localhost:8000'

  // Normalize: remove trailing slashes and trim
  let cleanUrl = url.trim().replace(/\/+$/, '')

  // Ensure protocol
  if (!/^https?:\/\//i.test(cleanUrl)) {
    cleanUrl = `http://${cleanUrl.replace(/^\/+/, '')}`
  }

  return cleanUrl
}

/**
 * Construct an absolute API URL
 * Ensures the URL is always properly formatted and absolute
 */
function buildApiUrl(path: string): string {
  const backend = getBackendUrl()
  const cleanPath = path.replace(/^\/+/, '')
  return `${backend}/${cleanPath}`
}

/**
 * Session State API
 */
export async function getSessionState(): Promise<SessionState | null> {
  // Only run on client-side
  if (typeof window === 'undefined') {
    return null
  }

  const url = buildApiUrl('/api/session/state')
  const { data } = await apiClient.get<SessionState>(url)
  return data
}

export async function updateSessionState(
  state: SessionStateUpdate
): Promise<SessionState | null> {
  // Fix: Don't build URL if window is undefined (SSR)
  if (typeof window === 'undefined') {
    return null
  }

  const url = buildApiUrl('/api/session/state')
  const { data } = await apiClient.put<SessionState>(url, state)
  return data
}

export async function deleteSessionState(): Promise<void> {
  const backend = getBackendUrl()
  await apiClient.delete(`${backend}/api/session/state`)
}

/**
 * Draft API
 */
export async function listDrafts(): Promise<DraftWork[]> {
  const backend = getBackendUrl()
  const { data } = await apiClient.get<{ drafts: DraftWork[] }>(
    `${backend}/api/drafts`
  )
  return data?.drafts || []
}

export async function getDraft(
  entityType: string,
  entityId: string
): Promise<DraftWork | null> {
  const backend = getBackendUrl()
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
  const backend = getBackendUrl()
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
  const backend = getBackendUrl()
  await apiClient.delete(`${backend}/api/drafts/${entityType}/${entityId}`)
}

/**
 * Offline Sync API
 */
export async function syncOfflineQueue(
  changes: OfflineChange[]
): Promise<SyncBatchResponse | null> {
  const backend = getBackendUrl()
  const { data } = await apiClient.post<SyncBatchResponse>(
    `${backend}/api/sync/batch`,
    { changes }
  )
  return data
}

export async function resolveConflict(
  resolution: ConflictResolution
): Promise<void> {
  const backend = getBackendUrl()
  await apiClient.post(`${backend}/api/sync/resolve`, resolution)
}

/**
 * Analytics API
 */
export async function recordWorkflowEvent(
  event: WorkflowAnalyticsEvent
): Promise<void> {
  if (typeof window === 'undefined') {
    return
  }

  const url = buildApiUrl('/api/analytics/workflow-event')
  await apiClient.post(url, event)
}
