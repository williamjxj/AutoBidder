# System Architecture Diagram

This Mermaid diagram shows the current high-level architecture of the Auto Bidder platform, including the dual Projects data paths (database persistence vs direct HuggingFace fallback).

## Architecture Overview

```mermaid
graph TB
    subgraph "Frontend (Next.js)"
        FE_DASH[Dashboard]
        FE_PROJECTS[Projects]
        FE_PROPOSALS[Proposals]
        FE_KB[Knowledge Base]
        FE_SETTINGS[Settings]
    end

    subgraph "Backend API (FastAPI Routers)"
        RT_AUTH["/auth"]
        RT_PROJECTS["/projects"]
        RT_PROPOSALS["/proposals + /draft"]
        RT_KB["/documents"]
        RT_ETL["/etl"]
        RT_KEYWORDS["/keywords"]
        RT_STRATEGIES["/strategies"]
        RT_SETTINGS["/settings"]
        RT_ANALYTICS["/analytics"]
    end

    subgraph "Core Services"
        SVC_PROJECT[project_service]
        SVC_DRAFT[draft_service]
        SVC_DOC[document_service]
        SVC_KEYWORD[keyword_service]
    end

    subgraph "ETL"
        ETL_SCHED[APScheduler]
        ETL_HF[hf_loader]
        ETL_FL[freelancer_loader]
        ETL_FILTER[domain_filter]
    end

    subgraph "Data Stores"
        DB[(PostgreSQL)]
        VDB[(ChromaDB)]
    end

    subgraph "External Providers"
        HF[HuggingFace datasets]
        FL[Freelancer scraping source]
        LLM[OpenAI / DeepSeek]
    end

    FE_DASH --> RT_ANALYTICS
    FE_DASH --> RT_PROJECTS
    FE_PROJECTS --> RT_PROJECTS
    FE_PROPOSALS --> RT_PROPOSALS
    FE_KB --> RT_KB
    FE_SETTINGS --> RT_SETTINGS

    RT_PROJECTS --> SVC_PROJECT
    RT_PROPOSALS --> SVC_DRAFT
    RT_KB --> SVC_DOC
    RT_KEYWORDS --> SVC_KEYWORD

    SVC_PROJECT --> DB
    SVC_DRAFT --> DB
    SVC_DOC --> DB
    SVC_DOC --> VDB
    SVC_DRAFT --> VDB
    SVC_DRAFT --> LLM

    ETL_SCHED --> ETL_HF
    ETL_SCHED --> ETL_FL
    ETL_HF --> HF
    ETL_FL --> FL
    ETL_HF --> ETL_FILTER
    ETL_FL --> ETL_FILTER
    ETL_FILTER --> SVC_PROJECT

    RT_PROJECTS -. fallback when persistence off .-> HF

    style DB fill:#336791,stroke:#333,stroke-width:2px
    style VDB fill:#ff6b6b,stroke:#333,stroke-width:2px
    style RT_PROJECTS fill:#00a896,stroke:#333,stroke-width:2px
    style ETL_SCHED fill:#f4a261,stroke:#333,stroke-width:2px
    style FE_PROJECTS fill:#61dafb,stroke:#333,stroke-width:2px
```

## Component Descriptions

### Notes

- `ETL_USE_PERSISTENCE=true`: Projects list/discover read and write through PostgreSQL via project service.
- `ETL_USE_PERSISTENCE=false`: Projects fallback can fetch directly from HuggingFace service for list/discover.
- Knowledge Base and proposal generation use PostgreSQL + ChromaDB together (metadata + vector retrieval).
- ETL scheduler can run both HF and Freelancer ingestion pipelines.
