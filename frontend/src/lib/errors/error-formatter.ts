/**
 * Error Formatter
 * 
 * Formats backend errors into actionable user messages.
 * Provides "what went wrong", "why it matters", and "how to fix" sections.
 */

export interface FormattedError {
  title: string
  whatWentWrong: string
  whyItMatters: string
  howToFix: string
  technicalDetails?: string
  severity: 'error' | 'warning' | 'info'
}

export class ErrorFormatter {
  /**
   * Format an error into a user-friendly message
   */
  format(error: any): FormattedError {
    // Network errors
    if (this.isNetworkError(error)) {
      return this.formatNetworkError(error)
    }

    // Validation errors (400)
    if (this.isValidationError(error)) {
      return this.formatValidationError(error)
    }

    // Authentication errors (401)
    if (this.isAuthError(error)) {
      return this.formatAuthError(error)
    }

    // Permission errors (403)
    if (this.isPermissionError(error)) {
      return this.formatPermissionError(error)
    }

    // Not found errors (404)
    if (this.isNotFoundError(error)) {
      return this.formatNotFoundError(error)
    }

    // Conflict errors (409)
    if (this.isConflictError(error)) {
      return this.formatConflictError(error)
    }

    // Server errors (500+)
    if (this.isServerError(error)) {
      return this.formatServerError(error)
    }

    // Generic error
    return this.formatGenericError(error)
  }

  /**
   * Check if error is a network error
   */
  private isNetworkError(error: any): boolean {
    return (
      error?.message?.includes('fetch') ||
      error?.message?.includes('network') ||
      error?.code === 'ECONNREFUSED' ||
      error?.code === 'NETWORK_ERROR' ||
      !navigator.onLine
    )
  }

  /**
   * Check if error is a validation error
   */
  private isValidationError(error: any): boolean {
    return error?.status === 400 || error?.response?.status === 400
  }

  /**
   * Check if error is an authentication error
   */
  private isAuthError(error: any): boolean {
    return error?.status === 401 || error?.response?.status === 401
  }

  /**
   * Check if error is a permission error
   */
  private isPermissionError(error: any): boolean {
    return error?.status === 403 || error?.response?.status === 403
  }

  /**
   * Check if error is a not found error
   */
  private isNotFoundError(error: any): boolean {
    return error?.status === 404 || error?.response?.status === 404
  }

  /**
   * Check if error is a conflict error
   */
  private isConflictError(error: any): boolean {
    return error?.status === 409 || error?.response?.status === 409
  }

  /**
   * Check if error is a server error
   */
  private isServerError(error: any): boolean {
    const status = error?.status || error?.response?.status
    return status >= 500 && status < 600
  }

  /**
   * Format network error
   */
  private formatNetworkError(error: any): FormattedError {
    return {
      title: 'Connection Problem',
      whatWentWrong: "We couldn't reach the server. Your internet connection may be unstable or the server may be temporarily unavailable.",
      whyItMatters: 'Your changes may not be saved, and you might not see the latest data.',
      howToFix: '1. Check your internet connection\n2. Try refreshing the page\n3. If the problem persists, contact support',
      technicalDetails: error?.message,
      severity: 'error',
    }
  }

  /**
   * Format validation error
   */
  private formatValidationError(error: any): FormattedError {
    const detail = error?.detail || error?.response?.data?.detail || 'Some fields have invalid values'
    
    return {
      title: 'Invalid Input',
      whatWentWrong: `The information you provided doesn't meet the requirements: ${detail}`,
      whyItMatters: 'We need correct information to process your request.',
      howToFix: '1. Review the highlighted fields\n2. Correct any invalid values\n3. Try submitting again',
      technicalDetails: JSON.stringify(error?.response?.data),
      severity: 'warning',
    }
  }

  /**
   * Format authentication error
   */
  private formatAuthError(error: any): FormattedError {
    return {
      title: 'Authentication Required',
      whatWentWrong: 'Your session has expired or you need to log in.',
      whyItMatters: 'You need to be logged in to perform this action.',
      howToFix: '1. Log in to your account\n2. If already logged in, try refreshing the page\n3. Contact support if the problem persists',
      technicalDetails: error?.message,
      severity: 'error',
    }
  }

  /**
   * Format permission error
   */
  private formatPermissionError(error: any): FormattedError {
    return {
      title: 'Access Denied',
      whatWentWrong: "You don't have permission to perform this action.",
      whyItMatters: 'Some features are restricted based on your account type or role.',
      howToFix: '1. Contact your administrator for access\n2. Upgrade your account if needed\n3. Contact support if you believe this is an error',
      technicalDetails: error?.message,
      severity: 'warning',
    }
  }

  /**
   * Format not found error
   */
  private formatNotFoundError(error: any): FormattedError {
    return {
      title: 'Not Found',
      whatWentWrong: 'The item you\'re looking for doesn\'t exist or has been deleted.',
      whyItMatters: 'You may be trying to access outdated or incorrect information.',
      howToFix: '1. Check that the URL is correct\n2. Go back and try again\n3. Contact support if you believe this is an error',
      technicalDetails: error?.message,
      severity: 'warning',
    }
  }

  /**
   * Format conflict error
   */
  private formatConflictError(error: any): FormattedError {
    return {
      title: 'Conflict Detected',
      whatWentWrong: 'Your changes conflict with recent updates. Someone else may have modified this item.',
      whyItMatters: 'We need to resolve the conflict to avoid losing data.',
      howToFix: '1. Refresh the page to see the latest version\n2. Reapply your changes\n3. Contact support if you need help merging changes',
      technicalDetails: JSON.stringify(error?.response?.data),
      severity: 'warning',
    }
  }

  /**
   * Format server error
   */
  private formatServerError(error: any): FormattedError {
    return {
      title: 'Server Error',
      whatWentWrong: 'Something went wrong on our end. This is not your fault.',
      whyItMatters: 'Your request couldn\'t be completed.',
      howToFix: '1. Try again in a few moments\n2. If the problem persists, contact support\n3. Our team has been notified and is working on it',
      technicalDetails: error?.message || JSON.stringify(error?.response?.data),
      severity: 'error',
    }
  }

  /**
   * Format generic error
   */
  private formatGenericError(error: any): FormattedError {
    return {
      title: 'Something Went Wrong',
      whatWentWrong: error?.message || 'An unexpected error occurred.',
      whyItMatters: 'Your request couldn\'t be completed.',
      howToFix: '1. Try again\n2. Refresh the page\n3. Contact support if the problem persists',
      technicalDetails: JSON.stringify(error),
      severity: 'error',
    }
  }

  /**
   * Get a short error message for inline display
   */
  getShortMessage(error: any): string {
    const formatted = this.format(error)
    return formatted.whatWentWrong
  }

  /**
   * Check if error should be shown to user
   */
  shouldShowToUser(error: any): boolean {
    // Don't show aborted requests
    if (error?.name === 'AbortError') return false
    
    // Don't show cancelled requests
    if (error?.message?.includes('cancel')) return false
    
    return true
  }
}

// Global instance
export const errorFormatter = new ErrorFormatter()
