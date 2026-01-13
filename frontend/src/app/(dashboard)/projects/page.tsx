/**
 * Projects Page
 * 
 * Lists user projects with filters and scroll position preservation.
 * Integrates with session context for state preservation across navigations.
 */

'use client'

import { useEffect, useState, useRef } from 'react'
import { useSessionState } from '@/hooks/useSessionState'
import { useNavigationTiming } from '@/hooks/useNavigationTiming'
import { LoadingSkeleton } from '@/components/workflow/progress-overlay'

interface ProjectFilters {
  search: string
  status: string
  sortBy: string
}

export default function ProjectsPage() {
  const { getFilters, setFilters, getScrollPosition, setScrollPosition, updateActiveEntity } = useSessionState()
  const { measureOperation } = useNavigationTiming()
  const [isLoading, setIsLoading] = useState(true)
  const [projects, setProjects] = useState<any[]>([])
  const scrollContainerRef = useRef<HTMLDivElement>(null)

  // Get saved filters from session state
  const savedFilters = getFilters<ProjectFilters>()
  const [filters, setLocalFilters] = useState<ProjectFilters>({
    search: savedFilters.search || '',
    status: savedFilters.status || 'all',
    sortBy: savedFilters.sortBy || 'updated',
  })

  // Load data and restore scroll position
  useEffect(() => {
    async function loadData() {
      setIsLoading(true)
      
      try {
        await measureOperation('load-projects', async () => {
          // Simulate API call
          await new Promise(resolve => setTimeout(resolve, 500))
          
          // TODO: Replace with actual API call
          setProjects([
            { id: '1', name: 'Sample Project 1', status: 'active', updated: '2024-01-10' },
            { id: '2', name: 'Sample Project 2', status: 'completed', updated: '2024-01-09' },
          ])
        })
      } catch (error) {
        console.error('Error loading projects:', error)
      } finally {
        setIsLoading(false)
      }
    }

    loadData()

    // Restore scroll position after content loads
    const restoreScroll = async () => {
      if (scrollContainerRef.current) {
        const savedPosition = getScrollPosition('/projects')
        if (savedPosition > 0) {
          scrollContainerRef.current.scrollTop = savedPosition
        }
      }
    }

    restoreScroll()
  }, [])

  // Save scroll position on scroll
  useEffect(() => {
    const container = scrollContainerRef.current
    if (!container) return

    const handleScroll = () => {
      const position = container.scrollTop
      setScrollPosition(position)
    }

    container.addEventListener('scroll', handleScroll)
    return () => container.removeEventListener('scroll', handleScroll)
  }, [setScrollPosition])

  // Save filters when they change
  useEffect(() => {
    setFilters(filters)
  }, [filters, setFilters])

  // Update active entity when viewing a project
  const handleProjectClick = (projectId: string) => {
    updateActiveEntity('project', projectId)
    // TODO: Navigate to project detail page
  }

  if (isLoading) {
    return (
      <div className="space-y-4">
        <h1 className="text-3xl font-bold">Projects</h1>
        <LoadingSkeleton lines={5} />
      </div>
    )
  }

  return (
    <div className="space-y-6" ref={scrollContainerRef}>
      <div>
        <h1 className="text-3xl font-bold">Projects</h1>
        <p className="text-muted-foreground mt-2">
          Manage your freelance projects and track their progress
        </p>
      </div>

      {/* Filters */}
      <div className="flex gap-4">
        <input
          type="text"
          placeholder="Search projects..."
          value={filters.search}
          onChange={(e) => setLocalFilters({ ...filters, search: e.target.value })}
          className="flex-1 rounded-md border border-slate-300 px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-900"
        />
        
        <select
          value={filters.status}
          onChange={(e) => setLocalFilters({ ...filters, status: e.target.value })}
          className="rounded-md border border-slate-300 px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-900"
        >
          <option value="all">All Status</option>
          <option value="active">Active</option>
          <option value="completed">Completed</option>
          <option value="archived">Archived</option>
        </select>

        <select
          value={filters.sortBy}
          onChange={(e) => setLocalFilters({ ...filters, sortBy: e.target.value })}
          className="rounded-md border border-slate-300 px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-900"
        >
          <option value="updated">Last Updated</option>
          <option value="created">Date Created</option>
          <option value="name">Name</option>
        </select>
      </div>

      {/* Projects List */}
      <div className="grid gap-4">
        {projects.length === 0 ? (
          <div className="rounded-lg border border-dashed border-slate-300 p-12 text-center dark:border-slate-700">
            <p className="text-muted-foreground">No projects found</p>
            <button className="mt-4 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90">
              Create Project
            </button>
          </div>
        ) : (
          projects.map((project) => (
            <div
              key={project.id}
              onClick={() => handleProjectClick(project.id)}
              className="cursor-pointer rounded-lg border border-slate-200 p-4 hover:border-primary hover:shadow-md transition-all dark:border-slate-800 dark:hover:border-primary"
            >
              <h3 className="font-semibold">{project.name}</h3>
              <div className="mt-2 flex items-center gap-4 text-sm text-muted-foreground">
                <span className="capitalize">{project.status}</span>
                <span>Updated: {project.updated}</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
