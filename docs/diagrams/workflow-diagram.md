# Projects and Proposal Workflow

This diagram reflects the implemented path from project discovery/listing to proposal generation and submission.

## Workflow Overview

```mermaid
graph TB
    U[User on Projects page]
    L1["GET /api/projects/list"]
    D1{ETL_USE_PERSISTENCE}
    DBR[Read projects from PostgreSQL]
    HFR[Fetch from HuggingFace adapter]
    RENDER[Render cards + filters + status badges]

    U --> L1 --> D1
    D1 -->|true| DBR --> RENDER
    D1 -->|false| HFR --> RENDER

    U --> DISC["POST /api/projects/discover"]
    D2{ETL_USE_PERSISTENCE}
    HFLOAD[HF loader + domain filter]
    UPSERT[Upsert into projects table]
    DBRET[Return records from DB]
    HFDIRECT[Return direct HF results]

    DISC --> D2
    D2 -->|true| HFLOAD --> UPSERT --> DBRET --> RENDER
    D2 -->|false| HFDIRECT --> RENDER

    RENDER --> GP[Generate Proposal click]
    GP --> STORE[Store project context in browser]
    STORE --> NEWP["/proposals/new"]
    NEWP --> GEN["POST /api/proposals/generate-from-job"]
    GEN --> RAG[RAG retrieval from ChromaDB + strategy + keywords]
    RAG --> LLM[LLM generation]
    LLM --> EDIT[User review and edit]
    EDIT --> SAVE["POST /api/proposals (draft/submitted)"]

    style U fill:#61dafb,stroke:#333,stroke-width:2px
    style DISC fill:#00a896,stroke:#333,stroke-width:2px
    style UPSERT fill:#f4a261,stroke:#333,stroke-width:2px
    style SAVE fill:#4caf50,stroke:#333,stroke-width:2px
```

## Detailed Stages

### 1. List and Discover

- `list` is the default browse/search path.
- `discover` is explicit fetch for new opportunities.
- In persistence mode, discover upserts then list reads stable DB state.

### 2. Project Context Transfer

- Selected project context is passed into Proposals flow.
- Applied IDs prevent accidental repeat application actions.

### 3. AI Proposal Generation

- Knowledge Base retrieval (ChromaDB) + strategy + keywords + job requirements.
- LLM returns generated sections for editing.

### 4. Save and Submit

- Draft and submitted proposals persist to database tables.
- Proposal records are then used by analytics and applied-state signals.

## Related Docs

- [projects.md](../projects.md)
- [proposals.md](../proposals.md)
- [huggingface-job-discovery.md](../huggingface-job-discovery.md)
