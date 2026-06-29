# Frontend Reference — Next.js 15 + React 19 + TanStack Query

## App Router Structure

```
frontend/src/
├── app/                    # Next.js App Router pages
│   ├── (auth)/             # Route group: login, register (no layout chrome)
│   ├── (dashboard)/        # Route group: protected pages with sidebar
│   │   ├── layout.tsx      # Dashboard shell — sidebar, header, auth guard
│   │   ├── page.tsx        # /dashboard (home)
│   │   ├── projects/       # /dashboard/projects
│   │   └── proposals/      # /dashboard/proposals
│   ├── api/                # Next.js Route Handlers (thin proxies to FastAPI)
│   └── layout.tsx          # Root layout — providers, fonts, metadata
├── components/
│   ├── ui/                 # shadcn/ui primitives (DO NOT edit these)
│   └── [feature]/          # Feature-specific components
├── hooks/                  # Custom React hooks (all TanStack Query hooks live here)
├── lib/
│   ├── api/                # API client functions (one file per domain)
│   └── utils.ts            # cn() and other shared utilities
└── types/                  # TypeScript type definitions
```

## Route Handler vs Direct API Call

Use Next.js Route Handlers (`app/api/`) sparingly — only when:
- You need to hide a secret from the browser (e.g., internal service key)
- You need server-side logic before forwarding to FastAPI

For everything else, call `NEXT_PUBLIC_API_URL` directly from the client. 
Don't add a proxy layer just for the sake of it.

## API Client Pattern

```typescript
// frontend/src/lib/api/proposals.ts
const BASE = process.env.NEXT_PUBLIC_API_URL;

function authHeaders() {
  const token = localStorage.getItem("access_token");
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

export async function generateProposal(payload: GenerateProposalInput) {
  const res = await fetch(`${BASE}/api/proposals/generate`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail ?? "Failed to generate proposal");
  }
  return res.json() as Promise<ProposalResponse>;
}
```

## TanStack Query Conventions

### Query key structure
```typescript
// Use arrays with domain → resource → id
["proposals"]                    // list
["proposals", id]                // single item
["proposals", "generate", jobId] // derived/computed resource
["knowledge", "stats"]           // nested resource
```

### Standard query hook
```typescript
export function useProposals() {
  return useQuery({
    queryKey: ["proposals"],
    queryFn: fetchProposals,
    staleTime: 1000 * 60 * 2, // 2 min — proposals don't change often
  });
}
```

### Optimistic update for status changes
```typescript
export function useUpdateProposalStatus() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) =>
      updateProposalStatus(id, status),
    onMutate: async ({ id, status }) => {
      await queryClient.cancelQueries({ queryKey: ["proposals"] });
      const previous = queryClient.getQueryData(["proposals"]);
      queryClient.setQueryData(["proposals"], (old: Proposal[]) =>
        old.map((p) => (p.id === id ? { ...p, status } : p))
      );
      return { previous };
    },
    onError: (_err, _vars, ctx) => {
      queryClient.setQueryData(["proposals"], ctx?.previous);
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["proposals"] });
    },
  });
}
```

## shadcn/ui Usage

Always use the installed component set — never reimplement from scratch.

```bash
# Add a new component (from project root)
cd frontend && npx shadcn@latest add <component-name>
```

Key components already installed (check `components/ui/` for the full list):
- `Button`, `Input`, `Textarea`, `Select`, `Checkbox`
- `Card`, `Badge`, `Separator`
- `Dialog`, `Sheet`, `Popover`, `DropdownMenu`
- `Table`, `Skeleton`, `Toast` (via `useToast`)
- `Form` (react-hook-form integration)

### Form pattern (shadcn Form + react-hook-form + zod)
```typescript
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Form, FormField, FormItem, FormLabel, FormControl, FormMessage } from "@/components/ui/form";

const schema = z.object({ jobDescription: z.string().min(50) });

function ProposalForm() {
  const form = useForm({ resolver: zodResolver(schema) });
  const generate = useGenerateProposal();

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit((data) => generate.mutate(data))}>
        <FormField name="jobDescription" control={form.control} render={({ field }) => (
          <FormItem>
            <FormLabel>Job Description</FormLabel>
            <FormControl><Textarea {...field} /></FormControl>
            <FormMessage />
          </FormItem>
        )} />
        <Button type="submit" disabled={generate.isPending}>
          {generate.isPending ? "Generating…" : "Generate Proposal"}
        </Button>
      </form>
    </Form>
  );
}
```

## Server Component Data Fetching

```typescript
// app/(dashboard)/proposals/page.tsx  — Server Component, no 'use client'
async function getProposals(token: string) {
  const res = await fetch(`${process.env.API_URL}/api/proposals`, {
    headers: { Authorization: `Bearer ${token}` },
    next: { revalidate: 60 }, // ISR: revalidate every 60s
  });
  if (!res.ok) throw new Error("Failed to load proposals");
  return res.json();
}

export default async function ProposalsPage() {
  const token = /* get from cookies/session */;
  const proposals = await getProposals(token);
  return <ProposalList proposals={proposals} />;
}
```
