---
name: autobidder-fullstack-dev
description: >
  Guides Claude when building, debugging, or extending features in the AutoBidder
  Next.js 15 + FastAPI codebase. Use this skill whenever the user mentions adding a
  feature, fixing a bug, writing an API endpoint, creating a React component, working
  on the frontend or backend code, asking about project conventions, setting up Docker,
  managing environment variables, or doing anything related to AutoBidder's tech stack
  (Next.js, FastAPI, TanStack Query, shadcn/ui, TailwindCSS, PostgreSQL, JWT auth,
  Resend, Vercel, Railway). Also trigger when the user shares a file path, pastes code
  from the project, or asks "how does X work in this project". Always consult this skill
  before writing any AutoBidder code — it encodes the project's conventions and will
  prevent pattern drift.
---

# AutoBidder — Full-Stack Development Guide

The AutoBidder repo is a monorepo with `frontend/` (Next.js 15) and `backend/` 
(FastAPI). Before writing any code, identify which layer is involved and read the 
relevant reference file.

## Quick Layer Router

| User says… | Read |
|---|---|
| component, page, route, UI, hook, query, mutation | `references/frontend.md` |
| endpoint, router, model, schema, migration, auth | `references/backend.md` |
| both layers / integration work | both reference files |
| docker, env vars, local setup, deploy | `references/infra.md` |

---

## Project-Wide Conventions

### File Naming
- Frontend: `kebab-case` for files/folders, `PascalCase` for components
- Backend: `snake_case` everywhere (files, functions, variables)
- Database: `snake_case` table and column names

### Environment Variables
- Frontend vars exposed to browser: prefix with `NEXT_PUBLIC_`
- Never hardcode secrets — all keys come from `.env.local` (frontend) or `.env` (backend)
- Docker Compose inherits from `.env` at repo root; see `references/infra.md`

### Error Handling Philosophy
- **Frontend:** TanStack Query handles loading/error states. Never use raw `try/catch` 
  in components — let query/mutation `isError` + `error` drive UI.
- **Backend:** All errors go through FastAPI's `HTTPException`. Raise, don't return 
  error dicts. Use the `handle_errors` decorator from `app/core/exceptions.py` for 
  consistent 4xx/5xx formatting.

### Auth Pattern
Every protected frontend route wraps in the `withAuth` HOC (or checks 
`useSession` hook). Every protected backend route uses the 
`get_current_user: User = Depends(get_current_user)` dependency.
Never bypass these — adding auth later is a pain.

---

## Workflow: Adding a New Feature

Follow these steps to add any feature cleanly:

### 1. Define the data shape first
Write the Pydantic request/response models in `backend/app/schemas/`.
This becomes the contract both layers share.

### 2. Add the database migration (if needed)
Write raw SQL in `database/migrations/`. Follow the existing naming pattern:
`NNNN_description.sql`. Apply with the script in `scripts/migrate.sh`.

### 3. Implement the backend endpoint
- Create or add to a router in `backend/app/routers/`
- Register it in `backend/app/main.py` under the appropriate prefix
- Write a quick manual test with curl before wiring the frontend

### 4. Wire the frontend
- Define the API call in `frontend/src/lib/api/` (one file per domain)
- Create TanStack Query hook in `frontend/src/hooks/`
- Build the component in `frontend/src/components/` or page in `frontend/src/app/`

### 5. Test the integration
- Run Docker Compose locally: `docker compose up --build`
- Check the browser network tab — confirm request shape matches Pydantic schema
- Confirm error states render correctly in UI

---

## Common Patterns (Quick Reference)

### FastAPI route with auth + error handling
```python
from fastapi import APIRouter, Depends, HTTPException
from app.core.auth import get_current_user
from app.schemas.proposal import ProposalCreate, ProposalResponse
from app.models.user import User

router = APIRouter(prefix="/proposals", tags=["proposals"])

@router.post("/", response_model=ProposalResponse)
async def create_proposal(
    body: ProposalCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Raise, don't return errors
    if not body.job_description:
        raise HTTPException(status_code=422, detail="job_description is required")
    ...
```

### TanStack Query mutation (frontend)
```typescript
// frontend/src/hooks/useGenerateProposal.ts
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { generateProposal } from "@/lib/api/proposals";

export function useGenerateProposal() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: generateProposal,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["proposals"] });
    },
  });
}
```

### shadcn/ui component with Tailwind 4
```tsx
// Always import from "@/components/ui/..." — never re-implement shadcn primitives
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

// TailwindCSS 4: use CSS variable tokens, not arbitrary values
// ✅  className="bg-background text-foreground"
// ❌  className="bg-[#ffffff] text-[#000000]"
```

### Next.js 15 App Router — Server vs Client components
```
// Rule of thumb:
// - Default to Server Component (no 'use client')
// - Add 'use client' ONLY when you need: useState, useEffect, event handlers,
//   browser APIs, or TanStack Query hooks
// - Data fetching in Server Components uses fetch() directly (no useQuery)
// - Data mutations always go in Client Components
```

For deeper patterns on each layer, read the relevant reference file listed in the
Quick Layer Router above.

---

## Debugging Checklist

When something is broken, work through this before asking for help:

**Frontend 4xx/5xx from API:**
1. Check browser Network tab — what's the exact status and response body?
2. Is the JWT token being sent? Check request headers for `Authorization: Bearer ...`
3. Does the request body shape match the Pydantic schema exactly?
4. Is `NEXT_PUBLIC_API_URL` set correctly in `.env.local`?

**Backend 500 errors:**
1. Check FastAPI logs: `docker compose logs backend -f`
2. Is the database connection alive? `docker compose ps` — is `db` healthy?
3. Did you run migrations after schema changes?
4. Is the `get_db` dependency returning a session (not None)?

**TanStack Query not refetching:**
1. Is `queryClient.invalidateQueries` called with the correct query key?
2. Are query keys consistent between the query hook and the invalidation call?
3. Is `staleTime` set too high in the query options?

**Docker Compose issues:**
1. Rebuild after dependency changes: `docker compose up --build`
2. Volume conflicts: `docker compose down -v` then `up --build`
3. Port conflicts: check `docker compose ps` and `lsof -i :3000` / `lsof -i :8000`
