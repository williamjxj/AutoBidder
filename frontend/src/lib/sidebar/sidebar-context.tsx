/**
 * Sidebar Context - Mobile menu state
 * Allows TopHeader to trigger mobile sidebar and AppSidebar to render it
 */

'use client'

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from 'react'

interface SidebarContextValue {
  mobileOpen: boolean
  desktopCollapsed: boolean
  openMobile: () => void
  closeMobile: () => void
  toggleMobile: () => void
  setDesktopCollapsed: (collapsed: boolean) => void
  toggleDesktopCollapsed: () => void
}

const SidebarContext = createContext<SidebarContextValue | null>(null)

const fallback: SidebarContextValue = {
  mobileOpen: false,
  desktopCollapsed: false,
  openMobile: () => {},
  closeMobile: () => {},
  toggleMobile: () => {},
  setDesktopCollapsed: () => {},
  toggleDesktopCollapsed: () => {},
}

export function useSidebar(): SidebarContextValue {
  const ctx = useContext(SidebarContext)
  return ctx ?? fallback
}

export function SidebarProvider({ children }: { children: ReactNode }) {
  const [mobileOpen, setMobileOpen] = useState(false)
  const [desktopCollapsed, setDesktopCollapsedState] = useState(false)

  useEffect(() => {
    const stored = window.localStorage.getItem('sidebar.desktopCollapsed')
    if (stored === 'true' || stored === 'false') {
      setDesktopCollapsedState(stored === 'true')
    }
  }, [])

  const openMobile = useCallback(() => setMobileOpen(true), [])
  const closeMobile = useCallback(() => setMobileOpen(false), [])
  const toggleMobile = useCallback(() => setMobileOpen((v) => !v), [])
  const setDesktopCollapsed = useCallback((collapsed: boolean) => {
    setDesktopCollapsedState(collapsed)
    window.localStorage.setItem(
      'sidebar.desktopCollapsed',
      collapsed ? 'true' : 'false'
    )
  }, [])
  const toggleDesktopCollapsed = useCallback(() => {
    setDesktopCollapsedState((value) => {
      const next = !value
      window.localStorage.setItem(
        'sidebar.desktopCollapsed',
        next ? 'true' : 'false'
      )
      return next
    })
  }, [])

  const value: SidebarContextValue = {
    mobileOpen,
    desktopCollapsed,
    openMobile,
    closeMobile,
    toggleMobile,
    setDesktopCollapsed,
    toggleDesktopCollapsed,
  }

  return (
    <SidebarContext.Provider value={value}>{children}</SidebarContext.Provider>
  )
}
