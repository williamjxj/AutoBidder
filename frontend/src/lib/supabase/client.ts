/**
 * Supabase Client - Browser/Client-Side
 * 
 * Use this client in Client Components, React hooks, and browser-side code.
 * Uses the anon key which is safe to expose publicly.
 */

import { createBrowserClient } from '@supabase/ssr'
import type { Database } from '@/types/database'

export function createClient() {
  return createBrowserClient<Database>(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
}

// Export a singleton instance for convenience
export const supabase = createClient()
