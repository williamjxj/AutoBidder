# Proposals — AI-Powered Bid Workflow

**Purpose:** Create, manage, submit proposals. RAG + Strategy + LLM for AI generation.

**Last Updated:** March 13, 2026

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

---

## AI Generate Inputs And Behavior

When you click **AI Generate**, multiple inputs are combined into a single prompt and retrieval flow.

### 1. Knowledge Base Documents

Knowledge Base content comes from documents uploaded via the Knowledge Base page. Each document belongs to a collection.

| Collection | Typical Use |
|------------|-------------|
| **Portfolio** | Project portfolios, demos, work samples |
| **Case Studies** | Success stories, before/after examples |
| **Team Profiles** | Bios, CVs, resumes |
| **Other** | General documents |

These documents are indexed for RAG and searched during proposal generation.

### 2. Knowledge Base Dropdown (Collection Selector)

On `/proposals/new`, the **Knowledge base** dropdown controls which collections are queried for RAG.

| Selection | What Gets Searched | Portfolio Docs Included? |
|-----------|-------------------|--------------------------|
| **All collections (default)** | All 4 collections | Yes |
| **Portfolio** | Only Portfolio | Yes |
| **Case Studies** | Only Case Studies | No |
| **Team Profiles** | Only Team Profiles | No |
| **Other** | Only Other (general_kb) | No |

### 3. Keywords

- Source: `/keywords`
- Behavior: all **active** keywords are included automatically
- Prompt intent: emphasize these skills when relevant

### 4. Required Skills

- Source: job description on the linked project/job
- Prompt intent: explicitly address skill requirements from the posting

### 5. Strategy

- Source: Strategies page
- Prompt intent: apply preferred tone and custom instruction style

### 6. End-To-End Binding

All inputs are used together during generation:

- Knowledge Base retrieval from selected collections
- Active keywords
- Required skills from the job
- Strategy instructions and tone

The generated proposal is expected to cite relevant experience, align to job needs, and reflect selected strategy constraints.

---

## Quick Reference

| Concept | Source | Used When |
|---------|--------|-----------|
| Knowledge Base | Uploaded documents | RAG context retrieval |
| Collection selector | Proposal form dropdown | Limits collection search scope |
| Keywords | Keywords page (active only) | Skills emphasis in output |
| Required skills | Job description | Requirement coverage in output |
| Strategy | Strategies page | Tone and instruction control |

---

## Related Documentation

- [Knowledge Base](./knowledge-base.md) - Upload, collections, ChromaDB
- [User Guides](./user-guides.md) - End-to-end usage flow
- [Database Schema Reference](./database-schema-reference.md) - Storage details
