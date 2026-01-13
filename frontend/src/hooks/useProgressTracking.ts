/**
 * useProgressTracking Hook
 * 
 * Tracks and displays progress for long-running operations.
 * Provides estimated completion time and progress percentage.
 */

'use client'

import { useState, useEffect, useCallback, useRef } from 'react'

export interface ProgressTrackingOptions {
  totalSteps?: number
  estimatedDurationMs?: number
  onComplete?: () => void
  autoStart?: boolean
}

export interface ProgressState {
  isActive: boolean
  currentStep: number
  totalSteps: number
  progress: number // 0-100
  elapsedMs: number
  estimatedRemainingMs: number
  message: string
}

/**
 * Hook to track progress of long-running operations
 */
export function useProgressTracking(options: ProgressTrackingOptions = {}) {
  const {
    totalSteps = 100,
    estimatedDurationMs = 0,
    onComplete,
    autoStart = false,
  } = options

  const [state, setState] = useState<ProgressState>({
    isActive: autoStart,
    currentStep: 0,
    totalSteps,
    progress: 0,
    elapsedMs: 0,
    estimatedRemainingMs: estimatedDurationMs,
    message: '',
  })

  const startTimeRef = useRef<number | null>(null)
  const intervalRef = useRef<NodeJS.Timeout>()

  /**
   * Start tracking progress
   */
  const start = useCallback((message: string = 'Processing...') => {
    startTimeRef.current = Date.now()
    setState({
      isActive: true,
      currentStep: 0,
      totalSteps,
      progress: 0,
      elapsedMs: 0,
      estimatedRemainingMs: estimatedDurationMs,
      message,
    })

    // Update elapsed time every 100ms
    intervalRef.current = setInterval(() => {
      if (startTimeRef.current) {
        const elapsed = Date.now() - startTimeRef.current
        setState((prev) => ({
          ...prev,
          elapsedMs: elapsed,
          estimatedRemainingMs: Math.max(0, estimatedDurationMs - elapsed),
        }))
      }
    }, 100)
  }, [totalSteps, estimatedDurationMs])

  /**
   * Update progress to specific step
   */
  const setStep = useCallback((step: number, message?: string) => {
    const progress = Math.min(100, (step / totalSteps) * 100)
    
    setState((prev) => {
      const newState = {
        ...prev,
        currentStep: step,
        progress,
      }
      
      if (message) {
        newState.message = message
      }
      
      return newState
    })

    // If completed, call onComplete
    if (step >= totalSteps && onComplete) {
      onComplete()
    }
  }, [totalSteps, onComplete])

  /**
   * Increment progress by one step
   */
  const increment = useCallback((message?: string) => {
    setState((prev) => {
      const newStep = Math.min(prev.totalSteps, prev.currentStep + 1)
      const progress = Math.min(100, (newStep / prev.totalSteps) * 100)
      
      const newState = {
        ...prev,
        currentStep: newStep,
        progress,
      }
      
      if (message) {
        newState.message = message
      }
      
      // If completed, call onComplete
      if (newStep >= prev.totalSteps && onComplete) {
        setTimeout(() => onComplete(), 0)
      }
      
      return newState
    })
  }, [onComplete])

  /**
   * Set progress percentage directly (0-100)
   */
  const setProgress = useCallback((percent: number, message?: string) => {
    const clampedPercent = Math.max(0, Math.min(100, percent))
    const step = Math.round((clampedPercent / 100) * totalSteps)
    
    setState((prev) => ({
      ...prev,
      currentStep: step,
      progress: clampedPercent,
      message: message || prev.message,
    }))

    // If completed, call onComplete
    if (clampedPercent >= 100 && onComplete) {
      onComplete()
    }
  }, [totalSteps, onComplete])

  /**
   * Complete the operation
   */
  const complete = useCallback((message: string = 'Complete!') => {
    setState((prev) => ({
      ...prev,
      currentStep: prev.totalSteps,
      progress: 100,
      message,
    }))

    // Clear interval
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
    }

    // Call onComplete
    if (onComplete) {
      onComplete()
    }

    // Reset after 2 seconds
    setTimeout(() => {
      setState((prev) => ({
        ...prev,
        isActive: false,
      }))
    }, 2000)
  }, [onComplete])

  /**
   * Reset progress
   */
  const reset = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
    }
    
    startTimeRef.current = null
    
    setState({
      isActive: false,
      currentStep: 0,
      totalSteps,
      progress: 0,
      elapsedMs: 0,
      estimatedRemainingMs: estimatedDurationMs,
      message: '',
    })
  }, [totalSteps, estimatedDurationMs])

  /**
   * Track a promise with automatic progress
   */
  const trackPromise = useCallback(
    async <T,>(
      promise: Promise<T>,
      message: string = 'Processing...'
    ): Promise<T> => {
      start(message)
      
      try {
        // Simulate progress while waiting
        const progressInterval = setInterval(() => {
          setState((prev) => {
            if (prev.progress < 90) {
              return {
                ...prev,
                progress: prev.progress + 5,
                currentStep: Math.round((prev.progress + 5) / 100 * prev.totalSteps),
              }
            }
            return prev
          })
        }, 300)

        const result = await promise
        
        clearInterval(progressInterval)
        complete('Success!')
        
        return result
      } catch (error) {
        if (intervalRef.current) {
          clearInterval(intervalRef.current)
        }
        
        setState((prev) => ({
          ...prev,
          message: 'Error occurred',
          isActive: false,
        }))
        
        throw error
      }
    },
    [start, complete]
  )

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [])

  return {
    ...state,
    start,
    setStep,
    increment,
    setProgress,
    complete,
    reset,
    trackPromise,
  }
}
