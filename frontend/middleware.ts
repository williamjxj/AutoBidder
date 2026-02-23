/**
 * Next.js Middleware - Authentication & Route Protection
 * 
 * Runs before every request to:
 * - Protect dashboard routes
 * - Redirect unauthenticated users to login
 */

import { NextResponse, type NextRequest } from 'next/server'

export async function middleware(request: NextRequest) {
  // Check for auth token in cookies (set by client-side after login)
  const token = request.cookies.get('auth_token')?.value
  
  // Protected routes - require authentication
  const protectedPaths = [
    '/dashboard',
    '/projects',
    '/proposals',
    '/knowledge-base',
    '/strategies',
    '/keywords',
    '/analytics',
    '/settings'
  ]
  
  const isProtectedRoute = protectedPaths.some(path => 
    request.nextUrl.pathname.startsWith(path)
  )
  
  // Redirect to login if accessing protected route without token
  if (isProtectedRoute && !token) {
    const loginUrl = new URL('/login', request.url)
    loginUrl.searchParams.set('redirect', request.nextUrl.pathname)
    return NextResponse.redirect(loginUrl)
  }
  
  // Redirect logged-in users away from auth pages
  const isAuthPage = request.nextUrl.pathname === '/login' || 
                     request.nextUrl.pathname === '/signup'
  
  if (isAuthPage && token) {
    return NextResponse.redirect(new URL('/dashboard', request.url))
  }
  
  return NextResponse.next()
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder
     * - External API calls (http:// or https://)
     * Note: Middleware only runs on same-origin requests, so external URLs won't be intercepted
     */
    '/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
  ],
}
