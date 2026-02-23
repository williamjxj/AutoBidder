# Strategic 12-Step Implementation Guide: "Auto-Bidder" Platform

This document provides a granular, technical walkthrough for merging the `bidmaster` and `biddingHub` projects and architecting the new AI-powered "Auto-Bidder" features.

---

## Phase 1: Infrastructure & Merge (Weeks 1-2)

### 1. Unified Next.js Foundation

- **Base**: Standardize on `bidmaster` (Next.js 15, PostgreSQL via docker-compose, Tailwind 4).
- **Environment**: Create a unified `.env` with JWT_SECRET, PostgreSQL connection, and OpenAI/Anthropic API keys.
- **Dependency Audit**: Align versions of React (v19), Shadcn/UI, and TanStack Query.

### 2. Database Migration & Schema Unification

- **Postgres Migration**: Port MySQL tables (`keywords`, `biddingStrategies`) from `biddingHub` to PostgreSQL.
- **pgvector Setup**: Enable the `vector` extension in PostgreSQL for RAG capabilities (via docker-compose).
- **Unified Pipeline Model**:
  - **Projects**: Store scraped job data.
  - **Proposals**: Store AI-generated drafts (formerly `bids` and `applications`).
  - **Knowledge Base**: New table for storing chunked embeddings of company history.

### 3. Feature Porting (Logic & UI)

- **Bidding Strategies**: Move the bidding logic from Express/tRPC (`biddingHub`) to Next.js Server Actions.
- **Keyword System**: Migration of the keyword monitoring dashboard.
- **Tailwind 4 Refactor**: Ensure all ported components from `biddingHub` use the new Tailwind 4 design tokens.

---

## Phase 2: Python Backend & Scraper (Weeks 3-4)

### 4. FastAPI Setup

- **Directory**: Initialize `/backend` using Python 3.11+.
- **Structure**: Modular routers for `/scraper`, `/rag`, and `/agent`.
- **Integration**: Use Pydantic v2 for shared data schemas between Python and Next.js.

### 5. Advanced Scraping with Crawlee (Python)

- **Platform Workers**:
  - **Upwork**: Implement a stealth scraper using `Crawlee` to manage proxies and headers.
  - **Freelancer/Tenders**: RSS/API consumers for public job feeds.
- **Normalization**: A processing pipeline that cleans HTML and extracts standard JSON schemas for job requirements.

### 6. Job Monitor & Alerting

- **Worker**: A background process that triggers every hour.
- **Matching Engine**: Simple semantic filter (or keyword filter) to push "High Value" jobs to the Next.js UI via WebSockets or polling.

---

## Phase 3: Vertical RAG & AI Agent (Weeks 5-6)

### 7. Company Knowledge Ingestion

- **PDF Pipeline**: A Python script to extract text from Case Studies, Resumes, and Portfolios using `PyMuPDF`.
- **Vectorization**: Generate embeddings (OpenAI `text-embedding-3-small`) and store them in ChromaDB via the backend service.

### 8. Vertical RAG Retrieval Logic

- **Context Fetcher**: When a job is selected, the Python backend retrieves the top 3-5 "matches" from the Knowledge Base that prove expertise in the specifically requested technologies.

### 9. AI Proposal Agent

- **Orchestration**: Use **LangGraph** or **PydanticAI** to manage the draft generation cycle.
- **Prompt Engineering**:
  - **System**: Roles (Expert IT Consulting Bidder).
  - **Evidence**: Inject retrieved knowledge chunks.
  - **Constraint**: Strict word counts and professional tone.
- **Agent Output**: Returns a structured JSON containing a draft, a summary, and references (evidence used).

---

## Phase 4: AI Studio UI & Verification (Weeks 7-8)

### 10. The AI Proposal Studio

- **Layout**: A split-screen editor in Next.js.
- **Interactive Features**:
  - "AI Rewrite" buttons for specific sections.
  - "Evidence Drawer" where users can drag-and-drop different case studies to swap them in the proposal.

### 11. End-to-End Orchestration

- **Workflow**:
    1. Scraper finds job -> PostgreSQL.
    2. Background Job -> Python FastAPI.
    3. FastAPI Agent -> Retrieves Context -> Generates Draft -> PostgreSQL.
    4. Next.js UI -> Polling or WebSocket update notifies user.

### 12. Quality Assurance & Performance

- **Validation**: Test the scraper against anti-bot measures.
- **RAG Tuning**: Optimize the `k` value for retrieval and improve chunking strategies for multi-page PDF case studies.
- **Latency**: Ensure AI generation doesn't block UI state.

---

> [!TIP]
> **Why this works**: By separating the "Brain" (Python/FastAPI/RAG) from the "Interface" (Next.js/PostgreSQL), we ensure the UI stays fast while the heavy-duty AI processing happens in a language suited for it.
