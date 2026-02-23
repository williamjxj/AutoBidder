# System Architecture Diagram

This Mermaid diagram shows the high-level architecture of the Auto Bidder platform.

## Architecture Overview

```mermaid
graph TB
    subgraph "Frontend - Next.js"
        UI[User Interface]
        Auth[Auth Pages]
        Dashboard[Dashboard]
        Proposals[Proposal Builder]
    end
    
    subgraph "Backend - FastAPI"
        API[FastAPI Server]
        AuthSvc[Auth Service]
        KeywordSvc[Keyword Service]
        DocSvc[Document Service]
        DraftSvc[Draft Service]
        StrategySvc[Strategy Service]
        VectorStore[Vector Store Service]
    end
    
    subgraph "Data Layer"
        PostgreSQL[(PostgreSQL)]
        ChromaDB[(ChromaDB Vector Store)]
    end
    
    subgraph "External Services"
        OpenAI[OpenAI GPT-4]
        DeepSeek[DeepSeek API]
        WebScraper[Web Scraper - Playwright]
    end
    
    UI --> API
    Auth --> AuthSvc
    Dashboard --> KeywordSvc
    Dashboard --> StrategySvc
    Proposals --> DraftSvc
    
    AuthSvc --> PostgreSQL
    KeywordSvc --> PostgreSQL
    KeywordSvc --> WebScraper
    DocSvc --> PostgreSQL
    DocSvc --> VectorStore
    DraftSvc --> VectorStore
    DraftSvc --> OpenAI
    DraftSvc --> DeepSeek
    StrategySvc --> PostgreSQL
    
    VectorStore --> ChromaDB
    
    style UI fill:#61dafb,stroke:#333,stroke-width:2px
    style API fill:#009688,stroke:#333,stroke-width:2px
    style PostgreSQL fill:#336791,stroke:#333,stroke-width:2px
    style ChromaDB fill:#ff6b6b,stroke:#333,stroke-width:2px
    style OpenAI fill:#10a37f,stroke:#333,stroke-width:2px
```

## Component Descriptions

### Frontend Layer
- **User Interface**: React-based UI built with Next.js 15 and shadcn/ui
- **Auth Pages**: Login/Signup with JWT authentication
- **Dashboard**: Project management, keyword tracking, strategy configuration
- **Proposal Builder**: Interactive proposal generation interface

### Backend Layer
- **FastAPI Server**: Main API gateway with async request handling
- **Auth Service**: JWT token management and user authentication
- **Keyword Service**: Keyword extraction and competitive analysis
- **Document Service**: Knowledge base document management
- **Draft Service**: AI-powered proposal generation
- **Strategy Service**: Bidding strategy configuration
- **Vector Store Service**: RAG-based semantic search

### Data Layer
- **PostgreSQL**: Primary relational database for structured data
- **ChromaDB**: Vector database for embeddings and semantic search

### External Services
- **OpenAI GPT-4**: Primary LLM for proposal generation
- **DeepSeek API**: Alternative LLM provider
- **Web Scraper**: Playwright-based scraper for competitive intelligence
