/**
 * Undo Toast Component
 * 
 * Shows success message with undo button and countdown timer.
 * Allows users to revert actions within a time-limited window.
 */

'use client'

import { useEffect, useState } from 'react'
import { Check, Undo2, X } from 'lucide-react'

export interface UndoToastProps {
  message: string
  onUndo: () => void
  onClose: () => void
  timeRemainingMs: number
  totalTimeMs?: number
}

/**
 * Toast showing success with undo option
 */
export function UndoToast({
  message,
  onUndo,
  onClose,
  timeRemainingMs,
  totalTimeMs = 5000,
}: UndoToastProps) {
  const [isUndoing, setIsUndoing] = useState(false)
  
  // Calculate progress percentage
  const progress = (timeRemainingMs / totalTimeMs) * 100

  const handleUndo = async () => {
    setIsUndoing(true)
    try {
      await onUndo()
      onClose()
    } catch (error) {
      console.error('Undo failed:', error)
      setIsUndoing(false)
    }
  }

  // Auto-close when time expires
  useEffect(() => {
    if (timeRemainingMs <= 0) {
      onClose()
    }
  }, [timeRemainingMs, onClose])

  return (
    <div
      className="rounded-lg border border-green-200 bg-green-50 p-4 shadow-lg dark:border-green-800 dark:bg-green-950 animate-in slide-in-from-top-2 duration-300"
      role="alert"
    >
      <div className="flex items-start gap-3">
        {/* Success icon */}
        <Check className="h-5 w-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
        
        <div className="flex-1 min-w-0">
          {/* Message */}
          <p className="text-sm font-medium text-green-900 dark:text-green-100">
            {message}
          </p>

          {/* Actions */}
          <div className="flex items-center gap-3 mt-2">
            {/* Undo button */}
            <button
              onClick={handleUndo}
              disabled={isUndoing || timeRemainingMs <= 0}
              className="flex items-center gap-1.5 text-sm font-medium text-green-700 hover:text-green-900 dark:text-green-300 dark:hover:text-green-100 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Undo2 className="h-3.5 w-3.5" />
              <span>{isUndoing ? 'Undoing...' : 'Undo'}</span>
            </button>

            {/* Time remaining */}
            <span className="text-xs text-green-600 dark:text-green-400">
              {Math.ceil(timeRemainingMs / 1000)}s
            </span>
          </div>

          {/* Progress bar */}
          <div className="mt-2 h-1 w-full overflow-hidden rounded-full bg-green-200 dark:bg-green-900">
            <div
              className="h-full bg-green-600 dark:bg-green-400 transition-all duration-100 ease-linear"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Close button */}
        <button
          onClick={onClose}
          className="flex-shrink-0 text-green-400 hover:text-green-600 dark:hover:text-green-200"
          aria-label="Close"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    </div>
  )
}

/**
 * Simple success toast without undo (for non-reversible actions)
 */
export function SuccessToast({
  message,
  onClose,
  autoClose = true,
  autoCloseDelay = 3000,
}: {
  message: string
  onClose: () => void
  autoClose?: boolean
  autoCloseDelay?: number
}) {
  useEffect(() => {
    if (!autoClose) return

    const timer = setTimeout(() => {
      onClose()
    }, autoCloseDelay)

    return () => clearTimeout(timer)
  }, [autoClose, autoCloseDelay, onClose])

  return (
    <div
      className="rounded-lg border border-green-200 bg-green-50 p-4 shadow-lg dark:border-green-800 dark:bg-green-950 animate-in slide-in-from-top-2 duration-300"
      role="alert"
    >
      <div className="flex items-start gap-3">
        <Check className="h-5 w-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
        
        <p className="flex-1 text-sm font-medium text-green-900 dark:text-green-100">
          {message}
        </p>

        <button
          onClick={onClose}
          className="flex-shrink-0 text-green-400 hover:text-green-600 dark:hover:text-green-200"
          aria-label="Close"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    </div>
  )
}

/**
 * Toast container for managing multiple toasts
 */
export function ToastContainer({
  toasts,
  onRemove,
}: {
  toasts: Array<{ id: string; component: React.ReactNode }>
  onRemove: (id: string) => void
}) {
  return (
    <div
      className="fixed top-4 right-4 z-50 flex flex-col gap-3 max-w-md w-full pointer-events-none"
      role="region"
      aria-label="Notifications"
    >
      {toasts.map(({ id, component }) => (
        <div key={id} className="pointer-events-auto">
          {component}
        </div>
      ))}
    </div>
  )
}
