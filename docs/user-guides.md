# User Guides — How to Start and Use the App

**Purpose:** Developer-focused guide for starting the app and using the UI.

---

## Starting the App

**Quick start (using Makefile):**
```bash
make infra-up      # Start PostgreSQL + ChromaDB
make install       # Install dependencies (one-time)
make dev           # Start both backend (:5555) and frontend (:5556)
```

**Or start individually:**
1. **Infrastructure:** `make infra-up`
2. **Backend:** `make backend-dev`
3. **Frontend:** `make frontend-dev`

See [setup-and-run.md](setup-and-run.md) for full setup or [makefile-commands.md](makefile-commands.md) for all available commands.

---

## Navigation

| Section | Purpose |
|---------|---------|
| **Dashboard** | Overview and stats |
| **Projects** | Discover jobs from HuggingFace → Generate Proposal |
| **Proposals** | Manage and submit AI-generated proposals |
| **Knowledge Base** | Upload portfolio PDFs/DOCX (used by RAG) |
| **Strategies** | AI prompt templates for different proposal tones |
| **Keywords** | Filter jobs by expertise |
| **Analytics** | Win rates and performance |
| **Settings** | Account and preferences |

---

## Core Workflow

### 1. Upload Knowledge Base (recommended first)

Go to **Knowledge Base** → Upload portfolio PDFs or DOCX. The AI uses these for RAG context when generating proposals.

### 2. Create or Select a Strategy

Go to **Strategies** → Create a strategy (e.g. "Professional", "Technical") or use default. This defines the tone and focus for AI-generated proposals.

### 3. Discover Jobs

Go to **Projects** → Click **Discover Jobs** → Enter keywords (optional) → Select dataset (optional) → Discover.

Jobs load from HuggingFace datasets (e.g. `jacob-hugging-face/job-descriptions`).

### 4. Generate Proposal

Click **Generate Proposal** on a job card. You are taken to the proposal form with job context pre-filled.

### 5. AI Generate (optional)

Click **AI Generate** next to the Description field. The backend uses RAG (your knowledge base) + strategy + LLM to produce a tailored proposal draft.

**Want to understand how it all connects?** See [AI Proposal Generation — Concepts](ai-proposal-generation-concepts.md) for how Knowledge Base, Keywords, Required Skills, and the Collection selector work together.

### 6. Submit

Review the proposal, edit if needed, then click **Submit Proposal**. The proposal is created directly from the form and saved to your Proposals list. Drafts auto-save in the background (~300ms) for recovery if you leave the page.

---

## Tips

- **No job linked:** If you go to `/proposals/new` directly, there is no job context. Use **Projects → Generate Proposal** to link a job.
- **AI Generate fails:** Ensure you have documents in Knowledge Base and a strategy selected. Check backend logs for 429 (rate limit) or API key errors.
- **Drafts:** Auto-saved drafts are kept 24 hours and can be recovered if you close the tab.

---

**Related:** [projects.md](projects.md) | [proposals.md](proposals.md) | [knowledge-base.md](knowledge-base.md) | [huggingface-job-discovery.md](huggingface-job-discovery.md)
