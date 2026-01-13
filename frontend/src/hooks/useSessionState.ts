/**
 * useSessionState Hook
 * 
 * Provides access to session state and methods for components.
 * Wraps the useWorkflowSession hook with convenient helpers.
 */

'use client'

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
  const activeEntity = sessionState
    ? {
        type: sessionState.active_entity_type,
        id: sessionState.active_entity_id,
      }
    : null

  /**
   * Get navigation history
   */
  const navigationHistory = sessionState?.navigation_history || []

  /**
   * Get scroll position for a path
   */
  const getScrollPosition = (path: string): number => {
    return sessionState?.scroll_position?.[path] || 0
  }

  /**
   * Set scroll position for current path
   */
  const setScrollPosition = async (position: number) => {
    if (!sessionState) return

    const newScrollPosition = {
      ...sessionState.scroll_position,
      [sessionState.current_path]: position,
    }

    await updateNavigation(
      sessionState.current_path,
      sessionState.active_entity_type || undefined,
      sessionState.active_entity_id || undefined
    )
  }

  /**
   * Get filters for current path
   */
  const getFilters = <T = Record<string, any>>(): T => {
    if (!sessionState?.current_path) return {} as T
    return (sessionState.filters?.[sessionState.current_path] as T) || ({} as T)
  }

  /**
   * Set filters for current path
   */
  const setFilters = async <T = Record<string, any>>(filters: T) => {
    if (!sessionState) return

    const newFilters = {
      ...sessionState.filters,
      [sessionState.current_path]: filters,
    }

    await updateNavigation(
      sessionState.current_path,
      sessionState.active_entity_type || undefined,
      sessionState.active_entity_id || undefined
    )
  }

  /**
   * Get UI state for current path
   */
  const getUIState = <T = Record<string, any>>(): T => {
    if (!sessionState?.current_path) return {} as T
    return (sessionState.ui_state?.[sessionState.current_path] as T) || ({} as T)
  }

  /**
   * Set UI state for current path
   */
  const setUIState = async <T = Record<string, any>>(uiState: T) => {
    if (!sessionState) return

    const newUIState = {
      ...sessionState.ui_state,
      [sessionState.current_path]: uiState,
    }

    await updateNavigation(
      sessionState.current_path,
      sessionState.active_entity_type || undefined,
      sessionState.active_entity_id || undefined
    )
  }

  /**
   * Navigate and record in history
   */
  const navigateWithHistory = async (
    path: string,
    entityType?: string,
    entityId?: string
  ) => {
    // Push current location to history before navigating
    if (sessionState?.current_path) {
      const entry: NavigationEntry = {
        path: sessionState.current_path,
        timestamp: new Date().toISOString(),
        entity_type: sessionState.active_entity_type || null,
        entity_id: sessionState.active_entity_id || null,
      }
      pushNavigation(entry)
    }

    // Update to new location
    await updateNavigation(path, entityType, entityId)
  }

  /**
   * Go back in navigation history
   */
  const goBack = () => {
    popNavigation()
  }

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
