# Proposals — AI-Powered Bid Workflow

**Purpose:** Create, manage, submit proposals. RAG + Strategy + LLM for AI generation.

---

## Workflow

1. **Projects** → Generate Proposal on job card
2. **Proposals/new** → Form pre-filled with job context (via sessionStorage/API)
3. **AI Generate** → RAG (ChromaDB) + strategy + LLM populate fields
4. **Auto-save** → Draft saved in background (300ms debounce, 24h retention)
5. **Submit** or **Save as Draft** → Persists to `proposals` table

---

## Features

| Feature | Description |
|---------|-------------|
| **AI Generate** | Job context + KB retrieval + strategy → LLM generates proposal |
| **Auto-save** | Debounced saves to `draft_work`; recovery banner on return |
| **Draft vs Submit** | Draft = visible in Proposals tab; Submit = final, triggers email |
| **Job Linking** | `project_id` / `job_identifier` links to project; prevents repeat apply |

---

## Key APIs

- `POST /api/proposals/generate-from-job` — AI generation
- `POST /api/proposals` — Create (draft or submitted)
- `GET /api/proposals` — List with status filter
- `GET /api/proposals/applied-ids` — Job IDs user already applied to

---

## Storage

- **proposals** — Final proposals (draft, submitted, accepted, rejected, withdrawn)
- **draft_work** — Auto-save work-in-progress (24h retention)

See [database-schema-reference.md](./database-schema-reference.md) for schema.
