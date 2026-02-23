# BidMaster Pro - Architecture Diagrams

Visual representations of the system architecture.

---

## 🏗️ Overall System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE                            │
│                     (Next.js 15 + shadcn/ui)                       │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │  Dashboard   │  │  Projects    │  │  Proposals   │            │
│  └──────────────┘  └──────────────┘  └──────────────┘            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │  Keywords    │  │  Strategies  │  │  Knowledge   │            │
│  └──────────────┘  └──────────────┘  │  Base        │            │
│                                       └──────────────┘            │
│                                                                     │
│  Hosted on: Vercel (https://bidmaster-pro.vercel.app)            │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTPS
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      AUTHENTICATION LAYER                           │
│                    (Custom JWT Authentication)                      │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  • Email/Password Auth                                       │  │
│  │  • JWT Token Management                                      │  │
│  │  • Session Tracking                                          │  │
│  │  • Bcrypt Password Hashing                                   │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   Next.js API    │  │  Python FastAPI  │  │  Job Scrapers    │
│    Routes        │  │  AI Service      │  │  Service         │
│                  │  │                  │  │                  │
│ /api/keywords    │  │ /api/rag/upload  │  │ Crawlee Engine   │
│ /api/strategies  │  │ /api/rag/query   │  │                  │
│ /api/proposals/  │  │ /api/proposals/  │  │ • Upwork API     │
│   generate       │  │   generate       │  │ • Freelancer API │
│                  │  │                  │  │ • Web Scraping   │
│                  │  │                  │  │                  │
│ Vercel Serverless│  │ Railway.app      │  │ Part of Python   │
└────────┬─────────┘  └────────┬─────────┘  │ Service          │
         │                     │             └────────┬─────────┘
         │                     │                      │
         ▼                     ▼                      │
┌──────────────────────────────────────────┐         │
│        PostgreSQL Database               │         │
│         (docker-compose)                 │         │
│                                          │         │
│  Tables:                                 │         │
│  ├─ users (custom table)                │         │
│  ├─ projects                             │◄────────┘
│  ├─ bids                                 │
│  ├─ keywords                             │
│  ├─ bidding_strategies                   │
│  ├─ platform_credentials                 │
│  └─ sources                              │
│                                          │
│  Auth: JWT tokens                        │
│  Backups: Manual or scheduled            │
└──────────────────────────────────────────┘
                     │
                     │
                     ▼
┌──────────────────────────────────────────┐
│      ChromaDB Vector Database            │
│      (RAG Knowledge Base)                │
│                                          │
│  Collections:                            │
│  ├─ case_studies                        │
│  │   └─ Past successful projects        │
│  ├─ team_profiles                       │
│  │   └─ Developer resumes, skills       │
│  └─ portfolio                            │
│      └─ Code samples, screenshots       │
│                                          │
│  Hosted on: Railway (persistent volume) │
└──────────────────────────────────────────┘
```

---

## 🔄 Auto-Bidding Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                 1. JOB DISCOVERY                            │
│                                                             │
│  ┌───────────┐      ┌───────────┐      ┌───────────┐      │
│  │  Upwork   │      │ Freelancer│      │  Others   │      │
│  └─────┬─────┘      └─────┬─────┘      └─────┬─────┘      │
│        │                  │                  │             │
│        └──────────────────┼──────────────────┘             │
│                           │                                │
│                           ▼                                │
│              ┌──────────────────────┐                      │
│              │  Crawlee Scraper     │                      │
│              │  • Rate limiting     │                      │
│              │  • Error handling    │                      │
│              │  • Proxy rotation    │                      │
│              └──────────┬───────────┘                      │
└─────────────────────────┼──────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                 2. PROJECT STORAGE                          │
│                                                             │
│              ┌──────────────────────┐                      │
│              │  PostgreSQL (docker-compose)             │
│              │  • Save project data │                      │
│              │  • Deduplicate       │                      │
│              │  • User filtering    │                      │
│              └──────────┬───────────┘                      │
└─────────────────────────┼──────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                 3. RAG CONTEXT RETRIEVAL                    │
│                                                             │
│              ┌──────────────────────┐                      │
│              │  Query ChromaDB      │                      │
│              │                      │                      │
│  Job Desc + Skills  ──────────┐    │                      │
│                               │    │                      │
│                               ▼    │                      │
│              ┌──────────────────────┐                      │
│              │  Vector Search       │                      │
│              │  (Embeddings)        │                      │
│              └──────────┬───────────┘                      │
│                         │                                  │
│                         ▼                                  │
│              ┌──────────────────────┐                      │
│              │  Retrieve:           │                      │
│              │  • Past projects     │                      │
│              │  • Team profiles     │                      │
│              │  • Success stories   │                      │
│              └──────────┬───────────┘                      │
└─────────────────────────┼──────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                 4. AI PROPOSAL GENERATION                   │
│                                                             │
│              ┌──────────────────────┐                      │
│              │  LLM (GPT-4)         │                      │
│              │                      │                      │
│  Inputs:                            │                      │
│  ├─ Job description                 │                      │
│  ├─ RAG context (past projects)     │                      │
│  ├─ Bidding strategy                │                      │
│  └─ Team expertise                  │                      │
│                │                    │                      │
│                ▼                    │                      │
│              ┌──────────────────────┐                      │
│              │  Generated Proposal: │                      │
│              │  ├─ Cover letter     │                      │
│              │  ├─ Technical approach                      │
│              │  ├─ Timeline         │                      │
│              │  └─ Relevant projects                       │
│              └──────────┬───────────┘                      │
└─────────────────────────┼──────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                 5. HUMAN REVIEW & SUBMISSION                │
│                                                             │
│              ┌──────────────────────┐                      │
│              │  Proposal Editor UI  │                      │
│              │  • Review proposal   │                      │
│              │  • Edit if needed    │                      │
│              │  • Submit or save    │                      │
│              └──────────┬───────────┘                      │
│                         │                                  │
│              ┌──────────┴───────────┐                      │
│              ▼                      ▼                      │
│     ┌──────────────┐       ┌──────────────┐              │
│     │  Submit via  │       │  Generate    │              │
│     │  Platform API│       │  Email Draft │              │
│     └──────────────┘       └──────────────┘              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🗄️ Database Schema Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                     users (custom table)                     │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  id (UUID, PK)                                         │  │
│  │  email                                                 │  │
│  │  password_hash                                         │  │
│  │  created_at                                            │  │
│  └────────────────────────────────────────────────────────┘  │
└─────────────────────┬────────────────────────────────────────┘
                      │
          ┌───────────┼───────────┬─────────────┬──────────┐
          │           │           │             │          │
          ▼           ▼           ▼             ▼          ▼
┌────────────────┐ ┌────────────────┐ ┌────────────────┐ ┌────────────────┐
│   projects     │ │   keywords     │ │ bidding_       │ │ platform_      │
│                │ │                │ │ strategies     │ │ credentials    │
├────────────────┤ ├────────────────┤ ├────────────────┤ ├────────────────┤
│ id (UUID, PK)  │ │ id (UUID, PK)  │ │ id (UUID, PK)  │ │ id (UUID, PK)  │
│ user_id (FK)   │ │ user_id (FK)   │ │ user_id (FK)   │ │ user_id (FK)   │
│ title          │ │ keyword        │ │ name           │ │ platform       │
│ description    │ │ description    │ │ system_prompt  │ │ api_key ⚠️     │
│ budget         │ │ is_active      │ │ tone           │ │ access_token⚠️ │
│ technologies[] │ │ created_at     │ │ focus_areas    │ │ expires_at     │
│ source_platform│ │                │ │ is_default     │ │ is_active      │
│ source_url     │ │                │ │                │ │                │
│ external_id    │ │                │ │                │ │                │
│ search_keyword │ │                │ │                │ │                │
│ client_rating  │ │                │ │                │ │                │
│ status         │ │                │ │                │ │                │
└────────┬───────┘ └────────────────┘ └────────────────┘ └────────────────┘
         │
         │
         ▼
┌────────────────┐
│     bids       │
├────────────────┤
│ id (UUID, PK)  │
│ project_id (FK)│───────────────────────┐
│ user_id (FK)   │                       │
│ bid_amount     │                       │
│ proposal       │                       │
│ cover_letter   │                       │
│ bidding_       │                       │
│   statement    │                       │
│ status         │                       │
│ submitted_at   │                       │
└────────────────┘                       │
                                         │
Legend:                                  │
PK = Primary Key                         │
FK = Foreign Key                         │
⚠️  = Encrypted field                    │
[] = Array field                         │
```

---

## 🔐 Security & Authentication Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT (Browser)                         │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │ 1. Login Request
                      ▼
┌─────────────────────────────────────────────────────────────┐
│             Backend FastAPI Auth Service (/api/auth)       │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Authentication Methods:                             │  │
│  │  • Email/Password (bcrypt hashing)                   │  │
│  │  • JWT Tokens (python-jose)                          │  │
│  │  • 7-day token expiration                            │  │
│  └──────────────────────────────────────────────────────┘  │
│                         │                                   │
│                         │ 2. Generate JWT                   │
│                         ▼                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  JWT Token (Signed with JWT_SECRET)                  │  │
│  │  {                                                   │  │
│  │    sub: "user-uuid",                                 │  │
│  │    email: "user@example.com",                        │  │
│  │    exp: <timestamp>,                                 │  │
│  │    iat: <timestamp>                                  │  │
│  │  }                                                   │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │ 3. Return JWT
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT (Browser)                         │
│  Stores JWT in:                                             │
│  • localStorage (frontend auth client)                      │
│  • HTTP-only cookie (for middleware)                        │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │ 4. API Request with JWT
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                 Next.js Middleware                          │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  1. Extract JWT from request                         │  │
│  │  2. Verify JWT signature                             │  │
│  │  3. Check expiration                                 │  │
│  │  4. Extract user_id                                  │  │
│  └──────────────────────────────────────────────────────┘  │
│                         │                                   │
│              ┌──────────┴──────────┐                        │
│              ▼                     ▼                        │
│        ┌─────────┐           ┌─────────┐                   │
│        │ Valid   │           │ Invalid │                   │
│        └────┬────┘           └────┬────┘                   │
│             │                     │                         │
│             │                     │                         │
│             ▼                     ▼                         │
│  ┌───────────────────┐  ┌───────────────────┐             │
│  │ Proceed to API    │  │ Return 401        │             │
│  └────────┬──────────┘  └───────────────────┘             │
└───────────┼─────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────┐
│               Database (Row Level Security)                 │
│                                                             │
│  PostgreSQL RLS Policies:                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  CREATE POLICY "Users can view their own projects"   │  │
│  │    ON projects FOR SELECT                            │  │
│  │    USING (auth.uid() = user_id);                     │  │
│  │                                                       │  │
│  │  CREATE POLICY "Users can insert their own projects" │  │
│  │    ON projects FOR INSERT                            │  │
│  │    WITH CHECK (auth.uid() = user_id);                │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  Result: Users can ONLY access their own data              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧠 RAG (Retrieval-Augmented Generation) Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                  KNOWLEDGE BASE UPLOAD                          │
│                                                                 │
│  User uploads:                                                  │
│  ├─ case_studies.pdf (past successful projects)                │
│  ├─ team_profiles.docx (developer resumes)                     │
│  └─ portfolio.pdf (code samples, screenshots)                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ 1. Upload to Next.js
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              DOCUMENT PROCESSING PIPELINE                       │
│                   (Python FastAPI Service)                      │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Step 1: Parse Documents                                  │  │
│  │  • pypdf for PDFs                                        │  │
│  │  • python-docx for DOCX                                  │  │
│  │  • Extract text content                                  │  │
│  └────────────────────────┬─────────────────────────────────┘  │
│                           │                                     │
│                           ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Step 2: Text Chunking (LangChain)                        │  │
│  │  • Chunk size: 1000 characters                           │  │
│  │  • Overlap: 200 characters                               │  │
│  │  • Preserve context across chunks                        │  │
│  └────────────────────────┬─────────────────────────────────┘  │
│                           │                                     │
│                           ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Step 3: Generate Embeddings (OpenAI)                     │  │
│  │  • Model: text-embedding-3-small                         │  │
│  │  • Vector dimension: 1536                                │  │
│  │  • Cost: $0.00002 per 1K tokens                          │  │
│  └────────────────────────┬─────────────────────────────────┘  │
│                           │                                     │
│                           ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Step 4: Store in ChromaDB                                │  │
│  │  • Collection: case_studies                              │  │
│  │  • Metadata: {project_name, skills, budget}              │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                         │
                         │ Stored
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ChromaDB Vector Store                        │
│                                                                 │
│  Collection: case_studies                                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Document 1:                                             │   │
│  │ • Text: "Built e-commerce platform for..."             │   │
│  │ • Vector: [0.23, -0.45, 0.67, ...]                      │   │
│  │ • Metadata: {project: "E-commerce", tech: ["React"]}    │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │ Document 2:                                             │   │
│  │ • Text: "AI chatbot with NLP capabilities..."          │   │
│  │ • Vector: [0.12, 0.89, -0.34, ...]                      │   │
│  │ • Metadata: {project: "AI Chatbot", tech: ["Python"]}   │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                         │
                         │ Query
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│               PROPOSAL GENERATION (with RAG)                    │
│                                                                 │
│  Input: New job posting                                         │
│  ├─ Title: "Build React E-commerce Dashboard"                  │
│  ├─ Skills: ["React", "TypeScript", "Node.js"]                 │
│  └─ Budget: $3000                                               │
│                         │                                       │
│                         ▼                                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Step 1: Generate Query Embedding                         │  │
│  │  Query: "React e-commerce project TypeScript Node.js"    │  │
│  │  → Vector: [0.25, -0.43, 0.69, ...]                      │  │
│  └────────────────────────┬─────────────────────────────────┘  │
│                           │                                     │
│                           ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Step 2: Vector Similarity Search (ChromaDB)              │  │
│  │  • Cosine similarity with stored vectors                 │  │
│  │  • Top K=5 most relevant documents                       │  │
│  │  • Results:                                              │  │
│  │    1. E-commerce platform (similarity: 0.92) ✅          │  │
│  │    2. React dashboard (similarity: 0.87) ✅              │  │
│  │    3. TypeScript API (similarity: 0.81) ✅               │  │
│  └────────────────────────┬─────────────────────────────────┘  │
│                           │                                     │
│                           ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Step 3: Context Assembly                                 │  │
│  │  Combine:                                                │  │
│  │  • Job description                                       │  │
│  │  • Retrieved context (past projects)                     │  │
│  │  • Bidding strategy                                      │  │
│  │  • Team profiles                                         │  │
│  └────────────────────────┬─────────────────────────────────┘  │
│                           │                                     │
│                           ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Step 4: LLM Generation (GPT-4)                           │  │
│  │  Prompt:                                                 │  │
│  │  ──────────────────────────────────────────────          │  │
│  │  System: You are a proposal writer. Use the context     │  │
│  │          below to demonstrate relevant experience.       │  │
│  │                                                          │  │
│  │  Context (from RAG):                                     │  │
│  │  - Built e-commerce platform with React, TypeScript...  │  │
│  │  - Developed payment gateway integration...             │  │
│  │  - Team has 5 years React experience...                 │  │
│  │                                                          │  │
│  │  Job: Build React E-commerce Dashboard...               │  │
│  │  ──────────────────────────────────────────────          │  │
│  │                                                          │  │
│  │  Output: ✅ Personalized, context-aware proposal         │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 Deployment Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                         PRODUCTION                               │
└──────────────────────────────────────────────────────────────────┘

                           Internet
                              │
                              │ HTTPS
                ┌─────────────┴─────────────┐
                │                           │
                ▼                           ▼
    ┌────────────────────┐      ┌────────────────────┐
    │   Vercel CDN       │      │  Railway.app       │
    │   (Edge Network)   │      │  (Cloud Platform)  │
    │                    │      │                    │
    │  Next.js Frontend  │      │  Python FastAPI    │
    │  • SSR/SSG         │      │  • AI Service      │
    │  • API Routes      │      │  • ChromaDB        │
    │  • Edge Functions  │      │  • Worker Process  │
    └──────┬─────────────┘      └──────┬─────────────┘
           │                           │
           │                           │
           │    ┌──────────────────────┤
           │    │                      │
           ▼    ▼                      ▼
    ┌──────────────────┐      ┌──────────────────┐
    │   PostgreSQL     │      │  External APIs   │
    │   (Database)     │      │                  │
    │                  │      │  • Upwork API    │
    │  • PostgreSQL    │      │  • Freelancer    │
    │  • ChromaDB      │      │  • OpenAI API    │
    │  • docker-compose│      └──────────────────┘
    └──────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                     COST BREAKDOWN                               │
├──────────────────────────────────────────────────────────────────┤
│  Vercel Pro:              $20/month                              │
│  PostgreSQL (Neon/AWS):   $20-25/month                           │
│  Railway (Python):        $20/month (with volume)                │
│  OpenAI API:              ~$150/month (100 users, caching)       │
│  Domain:                  $12/year                               │
│  ────────────────────────────────────────────────────            │
│  Total:                   ~$210-215/month                        │
│                                                                  │
│  Revenue (100 users):     $6,920/month                          │
│  Net Profit:              $6,705-6,710/month ($80,460/year)     │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Scaling Architecture (500+ Users)

```
                         Load Balancer
                              │
            ┌─────────────────┼─────────────────┐
            │                 │                 │
            ▼                 ▼                 ▼
    ┌────────────────┐ ┌────────────────┐ ┌────────────────┐
    │  Next.js       │ │  Next.js       │ │  Next.js       │
    │  Instance 1    │ │  Instance 2    │ │  Instance 3    │
    └────────────────┘ └────────────────┘ └────────────────┘
            │                 │                 │
            └─────────────────┼─────────────────┘
                              │
            ┌─────────────────┼─────────────────┐
            │                 │                 │
            ▼                 ▼                 ▼
    ┌────────────────┐ ┌────────────────┐ ┌────────────────┐
    │  Python AI     │ │  Python AI     │ │  Python AI     │
    │  Instance 1    │ │  Instance 2    │ │  Instance 3    │
    │  + ChromaDB    │ │  + ChromaDB    │ │  + ChromaDB    │
    └────────────────┘ └────────────────┘ └────────────────┘
            │                 │                 │
            └─────────────────┼─────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  PostgreSQL      │
                    │  (Read Replicas) │
                    │  + Redis Cache   │
                    └──────────────────┘
```

---

**Created**: January 12, 2026  
**Last Updated**: January 12, 2026  
**Version**: 1.0
