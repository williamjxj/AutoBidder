/**
 * useSessionState Hook
 * 
 * Provides access to session state and methods for components.
 * Wraps the useWorkflowSession hook with convenient helpers.
 */

import { useCallback, useMemo } from 'react'
import { useWorkflowSession } from '@/lib/workflow/session-context'
import type { NavigationEntry } from '@/types/workflow'

/**
 * Hook to access and update session state
 */
export function useSessionState() {
  const {
    sessionState,
    isLoading,
    isOnline,
    updateNavigation,
    updateActiveEntity,
    setFilters: contextSetFilters,
    setScrollPosition: contextSetScrollPosition,
    setUIState: contextSetUIState,
    pushNavigation,
    popNavigation,
    getNavigationHistory,
    clearSession,
    syncWithServer,
  } = useWorkflowSession()

  /**
   * Get current path
   */
  const currentPath = sessionState?.current_path || '/'

  /**
   * Get active entity
   */
  const activeEntity = useMemo(() => sessionState
    ? {
      type: sessionState.active_entity_type,
      id: sessionState.active_entity_id,
    }
    : null, [sessionState?.active_entity_type, sessionState?.active_entity_id])

  /**
   * Get navigation history
   */
  const navigationHistory = sessionState?.navigation_history || []

  /**
   * Get scroll position for a path
   */
  const getScrollPosition = useCallback((path: string): number => {
    return sessionState?.scroll_position?.[path] || 0
  }, [sessionState])

  /**
   * Set scroll position for current path
   */
  const setScrollPosition = useCallback(async (position: number) => {
    await contextSetScrollPosition(currentPath, position)
  }, [currentPath, contextSetScrollPosition])

  /**
   * Get filters for current path
   */
  const getFilters = useCallback(<T = Record<string, any>>(): T => {
    if (!sessionState?.filters || !currentPath) return {} as T
    return (sessionState.filters[currentPath] as T) || ({} as T)
  }, [sessionState?.filters, currentPath])

  /**
   * Set filters for current path
   */
  const setFilters = useCallback(async <T = Record<string, any>>(filters: T) => {
    await contextSetFilters(currentPath, filters)
  }, [currentPath, contextSetFilters])

  /**
   * Get UI state for current path
   */
  const getUIState = useCallback(<T = Record<string, any>>(): T => {
    if (!sessionState?.ui_state || !currentPath) return {} as T
    return (sessionState.ui_state[currentPath] as T) || ({} as T)
  }, [sessionState?.ui_state, currentPath])

  /**
   * Set UI state for current path
   */
  const setUIState = useCallback(async <T = Record<string, any>>(uiState: T) => {
    await contextSetUIState(currentPath, uiState)
  }, [currentPath, contextSetUIState])

  /**
   * Navigate and record in history
   */
  const navigateWithHistory = useCallback(async (
    path: string,
    entityType?: string,
    entityId?: string
  ) => {
    // Push current location to history before navigating
    if (currentPath) {
      const entry: NavigationEntry = {
        path: currentPath,
        timestamp: new Date().toISOString(),
        entity_type: activeEntity?.type || null,
        entity_id: activeEntity?.id || null,
      }
      pushNavigation(entry)
    }

    // Update to new location
    await updateNavigation(path, entityType, entityId)
  }, [currentPath, activeEntity, pushNavigation, updateNavigation])

  /**
   * Go back in navigation history
   */
  const goBack = useCallback(() => {
    popNavigation()
  }, [popNavigation])

  /**
   * Check if can go back
   */
  const canGoBack = navigationHistory.length > 0

  return {
    // State
    sessionState,
    isLoading,
    isOnline,
    currentPath,
    activeEntity,
    navigationHistory,
    canGoBack,

    // Navigation
    updateNavigation,
    updateActiveEntity,
    navigateWithHistory,
    goBack,

    // Scroll position
    getScrollPosition,
    setScrollPosition,

    // Filters
    getFilters,
    setFilters,

    // UI state
    getUIState,
    setUIState,

    // Session management
    clearSession,
    syncWithServer,
  }
}
