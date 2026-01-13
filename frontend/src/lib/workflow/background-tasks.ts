/**
 * Background Tasks Manager
 * 
 * Manages long-running operations in the background.
 * Allows users to continue working while tasks complete.
 */

type TaskStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'

export interface BackgroundTask<T = any> {
  id: string
  name: string
  description: string
  status: TaskStatus
  progress: number // 0-100
  result?: T
  error?: Error
  startedAt: Date
  completedAt?: Date
  onProgress?: (progress: number) => void
  onComplete?: (result: T) => void
  onError?: (error: Error) => void
}

export interface TaskExecutor<T = any> {
  (
    onProgress: (progress: number, message?: string) => void,
    signal: AbortSignal
  ): Promise<T>
}

export class BackgroundTasksManager {
  private tasks: Map<string, BackgroundTask> = new Map()
  private listeners: Set<(tasks: BackgroundTask[]) => void> = new Set()

  /**
   * Create and start a new background task
   */
  async createTask<T>(
    name: string,
    description: string,
    executor: TaskExecutor<T>,
    options: {
      onProgress?: (progress: number) => void
      onComplete?: (result: T) => void
      onError?: (error: Error) => void
    } = {}
  ): Promise<string> {
    const id = `task-${Date.now()}-${Math.random()}`
    const abortController = new AbortController()

    const task: BackgroundTask<T> = {
      id,
      name,
      description,
      status: 'pending',
      progress: 0,
      startedAt: new Date(),
      onProgress: options.onProgress,
      onComplete: options.onComplete,
      onError: options.onError,
    }

    this.tasks.set(id, task)
    this.notifyListeners()

    // Start execution
    this.executeTask(task, executor, abortController.signal)

    return id
  }

  /**
   * Execute a background task
   */
  private async executeTask<T>(
    task: BackgroundTask<T>,
    executor: TaskExecutor<T>,
    signal: AbortSignal
  ): Promise<void> {
    try {
      // Mark as running
      task.status = 'running'
      this.notifyListeners()

      // Progress callback
      const updateProgress = (progress: number, message?: string) => {
        task.progress = Math.max(0, Math.min(100, progress))
        if (message) {
          task.description = message
        }
        
        if (task.onProgress) {
          task.onProgress(progress)
        }
        
        this.notifyListeners()
      }

      // Execute the task
      const result = await executor(updateProgress, signal)

      // Mark as completed
      if (!signal.aborted) {
        task.status = 'completed'
        task.progress = 100
        task.result = result
        task.completedAt = new Date()

        if (task.onComplete) {
          task.onComplete(result)
        }

        this.notifyListeners()
      }
    } catch (error) {
      if (signal.aborted) {
        task.status = 'cancelled'
      } else {
        task.status = 'failed'
        task.error = error instanceof Error ? error : new Error(String(error))
        task.completedAt = new Date()

        if (task.onError) {
          task.onError(task.error)
        }
      }

      this.notifyListeners()
    }
  }

  /**
   * Cancel a running task
   */
  cancelTask(id: string): void {
    const task = this.tasks.get(id)
    if (task && task.status === 'running') {
      task.status = 'cancelled'
      task.completedAt = new Date()
      this.notifyListeners()
    }
  }

  /**
   * Get a task by ID
   */
  getTask(id: string): BackgroundTask | undefined {
    return this.tasks.get(id)
  }

  /**
   * Get all tasks
   */
  getAllTasks(): BackgroundTask[] {
    return Array.from(this.tasks.values())
  }

  /**
   * Get running tasks
   */
  getRunningTasks(): BackgroundTask[] {
    return Array.from(this.tasks.values()).filter(
      (task) => task.status === 'running' || task.status === 'pending'
    )
  }

  /**
   * Get completed tasks
   */
  getCompletedTasks(): BackgroundTask[] {
    return Array.from(this.tasks.values()).filter(
      (task) => task.status === 'completed'
    )
  }

  /**
   * Remove a task from the manager
   */
  removeTask(id: string): void {
    this.tasks.delete(id)
    this.notifyListeners()
  }

  /**
   * Clear all completed and failed tasks
   */
  clearFinishedTasks(): void {
    const toRemove = Array.from(this.tasks.values())
      .filter((task) => task.status === 'completed' || task.status === 'failed' || task.status === 'cancelled')
      .map((task) => task.id)

    toRemove.forEach((id) => this.tasks.delete(id))
    this.notifyListeners()
  }

  /**
   * Subscribe to task updates
   */
  subscribe(listener: (tasks: BackgroundTask[]) => void): () => void {
    this.listeners.add(listener)
    
    // Return unsubscribe function
    return () => {
      this.listeners.delete(listener)
    }
  }

  /**
   * Notify all listeners of task updates
   */
  private notifyListeners(): void {
    const tasks = this.getAllTasks()
    this.listeners.forEach((listener) => listener(tasks))
  }

  /**
   * Check if there are any running tasks
   */
  hasRunningTasks(): boolean {
    return this.getRunningTasks().length > 0
  }
}

// Global instance
export const backgroundTasksManager = new BackgroundTasksManager()

/**
 * Helper function to create a background task
 */
export async function runInBackground<T>(
  name: string,
  description: string,
  executor: TaskExecutor<T>,
  options: {
    onProgress?: (progress: number) => void
    onComplete?: (result: T) => void
    onError?: (error: Error) => void
  } = {}
): Promise<string> {
  return backgroundTasksManager.createTask(name, description, executor, options)
}

/**
 * Helper function to simulate a long-running task
 */
export async function simulateLongTask(
  name: string,
  durationMs: number = 5000,
  steps: number = 10
): Promise<string> {
  return runInBackground(
    name,
    'Processing...',
    async (onProgress) => {
      for (let i = 0; i <= steps; i++) {
        await new Promise((resolve) => setTimeout(resolve, durationMs / steps))
        onProgress((i / steps) * 100, `Step ${i + 1} of ${steps}`)
      }
      return { success: true, steps }
    }
  )
}
