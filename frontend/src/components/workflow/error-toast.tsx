/**
 * Error Toast Component
 * 
 * Displays errors with "what went wrong", "why it matters", and "how to fix" sections.
 * Provides actionable feedback to users.
 */

'use client'

import { useState, useEffect } from 'react'
import { X, AlertCircle, AlertTriangle, Info } from 'lucide-react'
import type { FormattedError } from '@/lib/errors/error-formatter'

export interface ErrorToastProps {
  error: FormattedError
  onClose: () => void
  autoClose?: boolean
  autoCloseDelay?: number
}

/**
 * Toast notification for errors with actionable information
 */
export function ErrorToast({
  error,
  onClose,
  autoClose = true,
  autoCloseDelay = 8000,
}: ErrorToastProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  // Auto-close after delay
  useEffect(() => {
    if (!autoClose) return

    const timer = setTimeout(() => {
      onClose()
    }, autoCloseDelay)

    return () => clearTimeout(timer)
  }, [autoClose, autoCloseDelay, onClose])

  // Icon based on severity
  const getIcon = () => {
    switch (error.severity) {
      case 'error':
        return <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400" />
      case 'warning':
        return <AlertTriangle className="h-5 w-5 text-amber-600 dark:text-amber-400" />
      case 'info':
        return <Info className="h-5 w-5 text-blue-600 dark:text-blue-400" />
    }
  }

  // Background color based on severity
  const getBgColor = () => {
    switch (error.severity) {
      case 'error':
        return 'border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-950'
      case 'warning':
        return 'border-amber-200 bg-amber-50 dark:border-amber-800 dark:bg-amber-950'
      case 'info':
        return 'border-blue-200 bg-blue-50 dark:border-blue-800 dark:bg-blue-950'
    }
  }

  return (
    <div
      className={`rounded-lg border p-4 shadow-lg ${getBgColor()} animate-in slide-in-from-top-2 duration-300`}
      role="alert"
    >
      <div className="flex items-start gap-3">
        {getIcon()}
        
        <div className="flex-1 min-w-0">
          {/* Title */}
          <h3 className="font-semibold text-sm">{error.title}</h3>
          
          {/* What went wrong */}
          <p className="text-sm mt-1 text-slate-700 dark:text-slate-300">
            {error.whatWentWrong}
          </p>

          {/* Expanded details */}
          {isExpanded && (
            <div className="mt-3 space-y-2 text-sm">
              {/* Why it matters */}
              <div>
                <p className="font-medium text-slate-900 dark:text-slate-100">
                  Why this matters:
                </p>
                <p className="text-slate-700 dark:text-slate-300 mt-0.5">
                  {error.whyItMatters}
                </p>
              </div>

              {/* How to fix */}
              <div>
                <p className="font-medium text-slate-900 dark:text-slate-100">
                  How to fix:
                </p>
                <div className="text-slate-700 dark:text-slate-300 mt-0.5 whitespace-pre-line">
                  {error.howToFix}
                </div>
              </div>

              {/* Technical details (if available) */}
              {error.technicalDetails && (
                <details className="mt-2">
                  <summary className="cursor-pointer text-xs font-medium text-slate-600 dark:text-slate-400">
                    Technical Details
                  </summary>
                  <pre className="mt-1 text-xs bg-slate-100 dark:bg-slate-900 p-2 rounded overflow-x-auto text-slate-700 dark:text-slate-300">
                    {error.technicalDetails}
                  </pre>
                </details>
              )}
            </div>
          )}

          {/* Expand/Collapse button */}
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-xs font-medium underline mt-2 text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100"
          >
            {isExpanded ? 'Show less' : 'Show more'}
          </button>
        </div>

        {/* Close button */}
        <button
          onClick={onClose}
          className="flex-shrink-0 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
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
export function ErrorToastContainer({
  errors,
  onRemove,
}: {
  errors: Array<{ id: string; error: FormattedError }>
  onRemove: (id: string) => void
}) {
  return (
    <div
      className="fixed top-4 right-4 z-50 flex flex-col gap-3 max-w-md w-full pointer-events-none"
      role="region"
      aria-label="Notifications"
    >
      {errors.map(({ id, error }) => (
        <div key={id} className="pointer-events-auto">
          <ErrorToast
            error={error}
            onClose={() => onRemove(id)}
          />
        </div>
      ))}
    </div>
  )
}
