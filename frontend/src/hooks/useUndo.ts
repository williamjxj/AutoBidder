/**
 * useUndo Hook
 * 
 * Implements undo functionality with 5-second window.
 * Allows reverting recent actions with time-limited availability.
 */

'use client'

import { useState, useCallback, useRef, useEffect } from 'react'

export interface UndoAction<T = any> {
  id: string
  description: string
  previousState: T
  undo: (previousState: T) => void | Promise<void>
  timestamp: number
}

export interface UseUndoOptions {
  windowMs?: number // Time window for undo (default: 5000ms)
  onUndo?: () => void
  onExpire?: () => void
}

export interface UseUndoReturn<T> {
  canUndo: boolean
  timeRemaining: number
  description: string | null
  registerAction: (action: Omit<UndoAction<T>, 'id' | 'timestamp'>) => void
  performUndo: () => Promise<void>
  clear: () => void
}

/**
 * Hook for undo functionality with time-limited window
 */
export function useUndo<T = any>(options: UseUndoOptions = {}): UseUndoReturn<T> {
  const {
    windowMs = 5000, // 5 seconds default
    onUndo,
    onExpire,
  } = options

  const [currentAction, setCurrentAction] = useState<UndoAction<T> | null>(null)
  const [timeRemaining, setTimeRemaining] = useState(0)
  const timerRef = useRef<NodeJS.Timeout>()
  const countdownRef = useRef<NodeJS.Timeout>()

  /**
   * Clear current undo action
   */
  const clear = useCallback(() => {
    setCurrentAction(null)
    setTimeRemaining(0)
    
    if (timerRef.current) {
      clearTimeout(timerRef.current)
    }
    
    if (countdownRef.current) {
      clearInterval(countdownRef.current)
    }
  }, [])

  /**
   * Register a new undoable action
   */
  const registerAction = useCallback(
    (action: Omit<UndoAction<T>, 'id' | 'timestamp'>) => {
      // Clear previous action
      clear()

      // Create new action with ID and timestamp
      const newAction: UndoAction<T> = {
        ...action,
        id: `undo-${Date.now()}-${Math.random()}`,
        timestamp: Date.now(),
      }

      setCurrentAction(newAction)
      setTimeRemaining(windowMs)

      // Set up countdown timer (update every 100ms for smooth progress)
      countdownRef.current = setInterval(() => {
        const elapsed = Date.now() - newAction.timestamp
        const remaining = Math.max(0, windowMs - elapsed)
        setTimeRemaining(remaining)

        if (remaining <= 0) {
          clear()
          if (onExpire) {
            onExpire()
          }
        }
      }, 100)

      // Set up expiration timer
      timerRef.current = setTimeout(() => {
        clear()
        if (onExpire) {
          onExpire()
        }
      }, windowMs)
    },
    [windowMs, clear, onExpire]
  )

  /**
   * Perform undo operation
   */
  const performUndo = useCallback(async () => {
    if (!currentAction) return

    try {
      // Execute undo function
      await currentAction.undo(currentAction.previousState)

      // Call onUndo callback
      if (onUndo) {
        onUndo()
      }

      // Clear the action
      clear()
    } catch (error) {
      console.error('Error performing undo:', error)
      throw error
    }
  }, [currentAction, onUndo, clear])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      clear()
    }
  }, [clear])

  return {
    canUndo: currentAction !== null && timeRemaining > 0,
    timeRemaining,
    description: currentAction?.description || null,
    registerAction,
    performUndo,
    clear,
  }
}

/**
 * Hook for managing multiple undo actions with history
 */
export function useUndoHistory<T = any>(options: UseUndoOptions = {}) {
  const [history, setHistory] = useState<UndoAction<T>[]>([])
  const undo = useUndo<T>(options)

  /**
   * Add action to history
   */
  const addToHistory = useCallback(
    (action: Omit<UndoAction<T>, 'id' | 'timestamp'>) => {
      undo.registerAction(action)
      
      setHistory((prev) => [
        ...prev,
        {
          ...action,
          id: `history-${Date.now()}-${Math.random()}`,
          timestamp: Date.now(),
        },
      ])

      // Keep only last 10 items in history
      if (history.length > 10) {
        setHistory((prev) => prev.slice(-10))
      }
    },
    [undo, history.length]
  )

  /**
   * Get history items
   */
  const getHistory = useCallback(() => {
    return history
  }, [history])

  /**
   * Clear history
   */
  const clearHistory = useCallback(() => {
    setHistory([])
    undo.clear()
  }, [undo])

  return {
    ...undo,
    history,
    addToHistory,
    getHistory,
    clearHistory,
  }
}
