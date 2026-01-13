# BidMaster Pro: Implementation Checklist

Quick reference for executing the merge and upgrade plan.

## ✅ Phase 1: Foundation Merge (Week 1)

### Day 1-2: Database Migration

```bash
# Navigate to BidMaster
cd /Users/william.jiang/my-experiments/bidding/bidmaster

# Create migration file
supabase migration new merge_biddinghub_features
```

**SQL to add** (in migration file):
- [ ] `keywords` table
- [ ] `bidding_strategies` table
- [ ] `platform_credentials` table
- [ ] Alter `projects` table (add `external_id`, `search_keyword`, `client_rating`)
- [ ] Alter `bids` table (add `cover_letter`, `bidding_statement`, `submission_method`)

```bash
# Apply migration
supabase db push

# Verify
supabase db inspect
```

### Day 3-5: Backend API Port

Create these files in `bidmaster/src/app/api/`:

- [ ] `keywords/route.ts` (GET, POST)
- [ ] `keywords/[id]/route.ts` (GET, PATCH, DELETE)
- [ ] `strategies/route.ts` (GET, POST)
- [ ] `strategies/[id]/route.ts` (GET, PATCH, DELETE)
- [ ] `proposals/generate/route.ts` (POST)

**Test each endpoint**:
```bash
# Test keywords
curl -X POST http://localhost:3000/api/keywords \
  -H "Content-Type: application/json" \
  -d '{"keyword":"react developer","description":"Frontend projects"}'

# Test proposal generation
curl -X POST http://localhost:3000/api/proposals/generate \
  -H "Content-Type: application/json" \
  -d '{"projectId":"xxx","strategyId":"xxx"}'
```

### Day 6-7: Frontend Feature Port

Create these files in `bidmaster/src/app/`:

- [ ] `keywords/page.tsx` - Keywords management
- [ ] `strategies/page.tsx` - Strategies management
- [ ] `proposals/[id]/page.tsx` - Proposal editor

Create these components in `bidmaster/src/components/`:

- [ ] `keyword-manager.tsx`
- [ ] `strategy-editor.tsx`
- [ ] `proposal-generator.tsx`

**Update navigation**:
- [ ] Add links to `app-sidebar.tsx`

---

## ✅ Phase 2: Python AI Service (Week 2)

### Day 1-2: Python Setup

```bash
# Create Python service directory
mkdir -p /Users/william.jiang/my-experiments/bidding/python-ai-service
cd python-ai-service

# Initialize Python environment
python3 -m venv venv
source venv/bin/activate

# Create requirements.txt
cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn==0.24.0
chromadb==0.4.18
langchain==0.1.0
openai==1.3.0
pypdf==3.17.1
python-docx==1.1.0
python-multipart==0.0.6
pydantic==2.5.0
psycopg2-binary==2.9.9
EOF

# Install dependencies
pip install -r requirements.txt

# Create directory structure
mkdir -p app/routers app/services app/models
touch app/__init__.py
touch app/main.py
touch app/config.py
```

### Day 3-4: RAG Implementation

Create these files:

- [ ] `app/main.py` - FastAPI app entry point
- [ ] `app/config.py` - Environment configuration
- [ ] `app/services/document_processor.py` - PDF/DOCX processing
- [ ] `app/services/vector_store.py` - ChromaDB operations
- [ ] `app/routers/rag.py` - RAG endpoints

**Test RAG pipeline**:
```bash
# Start service
uvicorn app.main:app --reload --port 8000

# Test upload
curl -X POST http://localhost:8000/api/rag/upload \
  -F "files=@test.pdf" \
  -F "collection=case_studies"
```

### Day 5-7: Proposal Generator

- [ ] `app/services/proposal_generator.py` - LLM + RAG logic
- [ ] `app/routers/proposals.py` - Proposal endpoints

**Test proposal generation**:
```bash
curl -X POST http://localhost:8000/api/proposals/generate \
  -H "Content-Type: application/json" \
  -d '{
    "job_title": "React Developer",
    "job_description": "Build a dashboard",
    "job_skills": ["React", "TypeScript"],
    "budget": "$3000",
    "strategy_id": "default"
  }'
```

---

## ✅ Phase 3: Advanced Features (Week 3)

### Day 1-3: Enhanced Scraping

- [ ] `app/services/crawler.py` - Crawlee implementation
- [ ] `app/routers/scraping.py` - Scraping endpoints
- [ ] Integrate with official APIs (Upwork, Freelancer)

### Day 4-5: Knowledge Base UI

In `bidmaster/src/`:

- [ ] `app/knowledge-base/page.tsx` - KB management page
- [ ] `components/knowledge-base-uploader.tsx` - File upload UI
- [ ] `app/api/ai/knowledge-base/upload/route.ts` - Upload proxy

### Day 6-7: Platform Integration

- [ ] Set up Upwork OAuth credentials
- [ ] Set up Freelancer API key
- [ ] Test direct bid submission
- [ ] Add credentials management UI

---

## ✅ Phase 4: Deploy (Week 4)

### Day 1-2: Testing

- [ ] End-to-end test: Upload KB → Scrape job → Generate proposal
- [ ] Test all CRUD operations
- [ ] Performance testing
- [ ] Error handling verification

### Day 3-4: Deployment

**Deploy Next.js**:
```bash
cd /Users/william.jiang/my-experiments/bidding/bidmaster
vercel --prod
```

**Deploy Python (Railway)**:
```bash
cd /Users/william.jiang/my-experiments/bidding/python-ai-service

# Install Railway CLI
npm i -g @railway/cli

# Deploy
railway login
railway init
railway up

# Set environment variables in Railway dashboard
# - OPENAI_API_KEY
# - SUPABASE_URL
# - SUPABASE_KEY
# - NEXTJS_URL
```

### Day 5-7: Documentation

- [ ] User guide (how to use the platform)
- [ ] API documentation (for developers)
- [ ] Video tutorial (screen recording)
- [ ] Update README.md

---

## Environment Variables Checklist

### Next.js (`.env.local`)

```bash
# Supabase
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=

# Python AI Service
PYTHON_AI_SERVICE_URL=

# OpenAI (optional, if calling from Next.js)
OPENAI_API_KEY=

# Platform APIs (optional)
UPWORK_API_KEY=
UPWORK_API_SECRET=
FREELANCER_API_KEY=
```

### Python Service (`.env`)

```bash
# OpenAI
OPENAI_API_KEY=

# Supabase (read-only)
SUPABASE_URL=
SUPABASE_KEY=

# ChromaDB
CHROMA_PERSIST_DIRECTORY=/app/chroma_db

# Platform APIs
UPWORK_API_KEY=
FREELANCER_API_KEY=

# CORS
NEXTJS_URL=https://bidmaster-pro.vercel.app
```

---

## Key Files Reference

### Files to Copy from BiddingHub

```bash
# Server files
biddingHub/server/_core/llm.ts → bidmaster/src/lib/llm.ts (adapt)
biddingHub/server/integrations/upwork.ts → python-ai-service/app/services/upwork.py (port)
biddingHub/server/integrations/freelancer.ts → python-ai-service/app/services/freelancer.py (port)

# Frontend pages (adapt to Next.js)
biddingHub/client/src/pages/Keywords.tsx → bidmaster/src/app/keywords/page.tsx
biddingHub/client/src/pages/Strategies.tsx → bidmaster/src/app/strategies/page.tsx
biddingHub/client/src/pages/ProposalEditor.tsx → bidmaster/src/app/proposals/[id]/page.tsx
```

### New Files to Create

**Python Service**:
```
python-ai-service/
├── app/
│   ├── main.py ✨
│   ├── config.py ✨
│   ├── routers/
│   │   ├── rag.py ✨
│   │   ├── proposals.py ✨
│   │   └── scraping.py ✨
│   └── services/
│       ├── document_processor.py ✨
│       ├── vector_store.py ✨
│       ├── proposal_generator.py ✨
│       └── crawler.py ✨
├── requirements.txt ✨
├── Dockerfile ✨
└── README.md ✨
```

**Next.js Updates**:
```
bidmaster/src/
├── app/
│   ├── keywords/page.tsx ✨
│   ├── strategies/page.tsx ✨
│   ├── proposals/[id]/page.tsx ✨
│   ├── knowledge-base/page.tsx ✨
│   └── api/
│       ├── keywords/route.ts ✨
│       ├── strategies/route.ts ✨
│       ├── proposals/generate/route.ts ✨
│       └── ai/
│           └── knowledge-base/upload/route.ts ✨
└── components/
    ├── keyword-manager.tsx ✨
    ├── strategy-editor.tsx ✨
    ├── proposal-generator.tsx ✨
    └── knowledge-base-uploader.tsx ✨
```

---

## Success Criteria

### Technical Milestones

- [ ] All BiddingHub features ported to BidMaster
- [ ] Python AI service deployed and accessible
- [ ] RAG system working (upload → embed → retrieve)
- [ ] Proposal generation < 30 seconds
- [ ] Frontend polish complete
- [ ] Zero critical bugs

### User Value Metrics

- [ ] Proposal generation time: 30min → 2min ✅
- [ ] Can upload 10+ knowledge base docs ✅
- [ ] Proposals include relevant past projects ✅
- [ ] Works with real Upwork/Freelancer data ✅

### Business Readiness

- [ ] Deployed to production ✅
- [ ] Pricing tiers defined ✅
- [ ] Payment integration (Stripe) ready ✅
- [ ] User documentation complete ✅

---

## Common Issues & Solutions

### Issue: ChromaDB not persisting data

**Solution**: Ensure persistent volume mounted
```python
# In vector_store.py
Settings(
    persist_directory="/app/chroma_db",  # Must be mounted volume in Railway
    anonymized_telemetry=False
)
```

### Issue: CORS errors between Next.js and Python

**Solution**: Update CORS middleware
```python
# In main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.NEXTJS_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: OpenAI API rate limits

**Solution**: Implement caching
```python
# Cache embeddings
@functools.lru_cache(maxsize=1000)
def get_embedding(text: str):
    return openai.Embedding.create(input=text, model="text-embedding-3-small")
```

### Issue: Supabase Row Level Security blocking API

**Solution**: Use service role key for server-side operations
```typescript
// In Next.js API route
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY! // Not anon key!
);
```

---

## Quick Start Commands

**Start Development Environment**:

```bash
# Terminal 1: Next.js
cd bidmaster
npm run dev

# Terminal 2: Python AI Service
cd python-ai-service
source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Terminal 3: Supabase (if local)
supabase start
```

**Run Tests**:

```bash
# Next.js
npm run lint
npm run type-check

# Python
pytest app/tests/

# End-to-end
npm run test:e2e
```

---

## Resource Links

- [Main Plan Document](./MERGE_AND_UPGRADE_PLAN.md)
- [BidMaster README](./bidmaster/README.md)
- [BiddingHub TODO](./biddingHub/todo.md)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [LangChain Docs](https://python.langchain.com/)
- [ChromaDB Docs](https://docs.trychroma.com/)
- [Next.js Docs](https://nextjs.org/docs)
- [Supabase Docs](https://supabase.com/docs)

---

**Last Updated**: January 12, 2026
