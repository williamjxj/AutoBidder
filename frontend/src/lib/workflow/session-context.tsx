/**
 * Workflow Session Context
 * 
 * Provides React Context for managing workflow session state across the application.
 * Handles navigation history, active entity tracking, and auto-save coordination.
 */

'use client'

import React, { createContext, useContext, useEffect, useState, useCallback } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import type { SessionState, NavigationEntry } from '@/types/workflow'
import { LocalStorage, BrowserSupport } from './storage-utils'
import { getSessionState, updateSessionState, recordWorkflowEvent } from '@/lib/api/client'

// Session Context Type
interface SessionContextType {
  sessionState: SessionState | null
  isLoading: boolean
  isOnline: boolean
  updateNavigation: (path: string, entityType?: string, entityId?: string) => Promise<void>
  updateActiveEntity: (entityType: string | null, entityId: string | null) => Promise<void>
  pushNavigation: (entry: NavigationEntry) => void
  popNavigation: () => void
  getNavigationHistory: () => NavigationEntry[]
  clearSession: () => Promise<void>
  syncWithServer: () => Promise<void>
}

const SessionContext = createContext<SessionContextType | null>(null)

// Local storage key
const SESSION_STORAGE_KEY = 'workflow-session-state'
const SYNC_INTERVAL_MS = 30000 // Sync every 30 seconds

/**
 * Session Context Provider
 */
export function WorkflowProvider({ children }: { children: React.ReactNode }) {
  const [sessionState, setSessionState] = useState<SessionState | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isOnline, setIsOnline] = useState(true)
  const router = useRouter()
  const pathname = usePathname()

  // Check browser support on mount
  useEffect(() => {
    const support = BrowserSupport.getSupport()
    if (!support.localStorage) {
      console.warn('localStorage not available - session state will not persist')
    }
    if (!support.indexedDB) {
      console.warn('IndexedDB not available - offline features disabled')
    }
  }, [])

  // Initialize session state from localStorage or server
  useEffect(() => {
    async function initSession() {
      try {
        // Try loading from localStorage first (faster)
        const cached = LocalStorage.get<SessionState | null>(SESSION_STORAGE_KEY, null)
        
        if (cached) {
          setSessionState(cached)
          setIsLoading(false)
          
          // Sync with server in background
          syncWithServer()
        } else {
          // Load from server
          const serverState = await getSessionState()
          if (serverState) {
            setSessionState(serverState)
            LocalStorage.set(SESSION_STORAGE_KEY, serverState)
          }
          setIsLoading(false)
        }
      } catch (error) {
        console.error('Error initializing session:', error)
        setIsLoading(false)
      }
    }

    initSession()
  }, [])

  // Monitor online/offline status
  useEffect(() => {
    if (!BrowserSupport.hasOnlineEvents()) return

    function handleOnline() {
      setIsOnline(true)
      syncWithServer() // Sync when coming back online
    }

    function handleOffline() {
      setIsOnline(false)
    }

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    // Set initial state
    setIsOnline(navigator.onLine)

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  // Periodic sync with server
  useEffect(() => {
    if (!sessionState || !isOnline) return

    const interval = setInterval(() => {
      syncWithServer()
    }, SYNC_INTERVAL_MS)

    return () => clearInterval(interval)
  }, [sessionState, isOnline])

  // Track route changes
  useEffect(() => {
    if (!sessionState || !pathname) return

    // Only track dashboard routes
    if (pathname.startsWith('/dashboard')) {
      updateNavigation(pathname)
    }
  }, [pathname])

  /**
   * Sync session state with server
   */
  const syncWithServer = useCallback(async () => {
    if (!sessionState || !isOnline) return

    try {
      const updated = await updateSessionState({
        current_path: sessionState.current_path,
        navigation_history: sessionState.navigation_history,
        active_entity_type: sessionState.active_entity_type,
        active_entity_id: sessionState.active_entity_id,
        scroll_position: sessionState.scroll_position,
        filters: sessionState.filters,
        ui_state: sessionState.ui_state,
      })

      if (updated) {
        setSessionState(updated)
        LocalStorage.set(SESSION_STORAGE_KEY, updated)
      }
    } catch (error) {
      console.error('Error syncing session with server:', error)
    }
  }, [sessionState, isOnline])

  /**
   * Update navigation state
   */
  const updateNavigation = useCallback(
    async (path: string, entityType?: string, entityId?: string) => {
      const newState: SessionState = {
        ...sessionState,
        id: sessionState?.id || crypto.randomUUID(),
        user_id: sessionState?.user_id || '',
        current_path: path,
        active_entity_type: entityType || null,
        active_entity_id: entityId || null,
        navigation_history: sessionState?.navigation_history || [],
        scroll_position: sessionState?.scroll_position || {},
        filters: sessionState?.filters || {},
        ui_state: sessionState?.ui_state || {},
        created_at: sessionState?.created_at || new Date().toISOString(),
        updated_at: new Date().toISOString(),
      }

      setSessionState(newState)
      LocalStorage.set(SESSION_STORAGE_KEY, newState)

      // Sync with server if online
      if (isOnline) {
        try {
          await updateSessionState(newState)
        } catch (error) {
          console.error('Error updating navigation on server:', error)
        }
      }

      // Record analytics event
      await recordWorkflowEvent({
        event_type: 'navigation',
        entity_type: entityType || null,
        entity_id: entityId || null,
        metadata: { from: sessionState?.current_path, to: path },
      })
    },
    [sessionState, isOnline]
  )

  /**
   * Update active entity
   */
  const updateActiveEntity = useCallback(
    async (entityType: string | null, entityId: string | null) => {
      if (!sessionState) return

      const newState: SessionState = {
        ...sessionState,
        active_entity_type: entityType,
        active_entity_id: entityId,
        updated_at: new Date().toISOString(),
      }

      setSessionState(newState)
      LocalStorage.set(SESSION_STORAGE_KEY, newState)

      if (isOnline) {
        try {
          await updateSessionState(newState)
        } catch (error) {
          console.error('Error updating active entity on server:', error)
        }
      }
    },
    [sessionState, isOnline]
  )

  /**
   * Push navigation entry to history
   */
  const pushNavigation = useCallback(
    (entry: NavigationEntry) => {
      if (!sessionState) return

      const history = [...(sessionState.navigation_history || []), entry]
      
      // Keep only last 50 entries
      const trimmedHistory = history.slice(-50)

      const newState: SessionState = {
        ...sessionState,
        navigation_history: trimmedHistory,
        updated_at: new Date().toISOString(),
      }

      setSessionState(newState)
      LocalStorage.set(SESSION_STORAGE_KEY, newState)
    },
    [sessionState]
  )

  /**
   * Pop navigation entry from history
   */
  const popNavigation = useCallback(() => {
    if (!sessionState || !sessionState.navigation_history?.length) return

    const history = [...sessionState.navigation_history]
    const previousEntry = history.pop()

    const newState: SessionState = {
      ...sessionState,
      navigation_history: history,
      updated_at: new Date().toISOString(),
    }

    setSessionState(newState)
    LocalStorage.set(SESSION_STORAGE_KEY, newState)

    // Navigate to previous path
    if (previousEntry?.path) {
      router.push(previousEntry.path)
    }
  }, [sessionState, router])

  /**
   * Get navigation history
   */
  const getNavigationHistory = useCallback(() => {
    return sessionState?.navigation_history || []
  }, [sessionState])

  /**
   * Clear session state
   */
  const clearSession = useCallback(async () => {
    setSessionState(null)
    LocalStorage.remove(SESSION_STORAGE_KEY)

    if (isOnline) {
      try {
        // Server-side clear will be implemented in user story tasks
        // await deleteSessionState()
      } catch (error) {
        console.error('Error clearing session on server:', error)
      }
    }
  }, [isOnline])

  const value: SessionContextType = {
    sessionState,
    isLoading,
    isOnline,
    updateNavigation,
    updateActiveEntity,
    pushNavigation,
    popNavigation,
    getNavigationHistory,
    clearSession,
    syncWithServer,
  }

  return (
    <SessionContext.Provider value={value}>
      {children}
    </SessionContext.Provider>
  )
}

/**
 * Hook to access session context
 */
export function useWorkflowSession() {
  const context = useContext(SessionContext)
  
  if (!context) {
    throw new Error('useWorkflowSession must be used within WorkflowProvider')
  }
  
  return context
}
