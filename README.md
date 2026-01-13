# Auto-Bidder Platform 🤖

An AI-powered auto-bidding platform that reduces proposal writing time from 30 minutes to 2 minutes using RAG-based knowledge retrieval and AI proposal generation.

## 🎯 Core Features

- **Automated Job Discovery**: Scrape and collect relevant freelance jobs from multiple platforms
- **Smart Knowledge Base**: Upload portfolio documents, case studies, and team profiles for AI context
- **AI Proposal Generation**: Generate personalized, evidence-based proposals in under 60 seconds
- **Bidding Strategies**: Create reusable AI prompt templates for different proposal styles
- **Keyword Management**: Filter jobs based on your expertise and preferences
- **Analytics Dashboard**: Track win rates, platform performance, and time savings

## 🏗️ Architecture

This is a **full-stack monorepo** with two main components:

### Frontend (Next.js 15)

- **Framework**: Next.js 15 with App Router
- **UI**: React 19 + shadcn/ui + TailwindCSS 4
- **State**: TanStack Query for server state
- **Auth**: Supabase Auth
- **Database**: PostgreSQL via Supabase

### Backend (Python FastAPI)

- **Framework**: FastAPI 0.104+
- **Vector DB**: ChromaDB for RAG
- **RAG**: LangChain for document processing
- **LLM**: OpenAI GPT-4-turbo
- **Scraping**: Crawlee for job discovery

## 🚀 Quick Start

### Prerequisites

- Node.js 20+
- Python 3.11+
- Supabase CLI
- Docker (optional)

### Setup (5 minutes)

```bash
# Clone the repository
git clone <repo-url> auto-bidder
cd auto-bidder

# Setup frontend
cd frontend
npm install
cp .env.example .env.local
# Edit .env.local with your Supabase credentials
npm run dev  # Runs on :3000

# Setup backend (new terminal)
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your OpenAI API key
uvicorn app.main:app --reload --port 8000

# Setup database (new terminal)
supabase start  # Starts local Supabase
supabase db reset  # Applies migrations
```

### Environment Variables

**Frontend** (`.env.local`):

- `NEXT_PUBLIC_SUPABASE_URL`: Your Supabase project URL
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`: Supabase anon key
- `PYTHON_AI_SERVICE_URL`: Python service URL (default: <http://localhost:8000>)

**Backend** (`.env`):

- `OPENAI_API_KEY`: Your OpenAI API key
- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_SERVICE_KEY`: Supabase service role key
- `CHROMA_PERSIST_DIR`: ChromaDB storage path (default: ./chroma_db)

## 📚 Documentation

Comprehensive documentation is available in the [`docs/`](./docs/) directory:

- [**START_HERE.md**](./docs/START_HERE.md) - Project overview and getting started
- [**implementation.md**](./docs/implementation.md) - 12-step implementation guide
- [**ARCHITECTURE_DIAGRAM.md**](./docs/ARCHITECTURE_DIAGRAM.md) - Visual system architecture
- [**MERGE_AND_UPGRADE_PLAN.md**](./docs/MERGE_AND_UPGRADE_PLAN.md) - Detailed merge strategy
- [**IMPLEMENTATION_CHECKLIST.md**](./docs/IMPLEMENTATION_CHECKLIST.md) - Week-by-week checklist

## 🗂️ Project Structure

```
auto-bidder/
├── frontend/              # Next.js 15 application
│   ├── src/
│   │   ├── app/           # Next.js App Router
│   │   ├── components/    # React components
│   │   ├── lib/           # Utilities
│   │   └── hooks/         # Custom hooks
│   └── package.json
├── backend/               # Python AI service
│   ├── app/
│   │   ├── main.py        # FastAPI entry
│   │   ├── routers/       # API routes
│   │   ├── services/      # Business logic
│   │   └── models/        # Pydantic schemas
│   └── requirements.txt
├── database/              # Database migrations
│   ├── migrations/
│   └── seed/
├── shared/                # Shared types
│   └── types/
├── scripts/               # Automation scripts
│   ├── setup/
│   └── deploy/
└── docs/                  # Documentation
```

## 🧪 Testing

```bash
# Frontend tests
cd frontend
npm test

# Backend tests
cd backend
pytest

# E2E tests
npm run test:e2e
```

## 🚢 Deployment

### Frontend (Vercel)

```bash
cd frontend
vercel deploy
```

### Backend (Railway)

```bash
cd backend
railway up
```

See [docs/DEPLOYMENT.md](./docs/DEPLOYMENT.md) for detailed deployment instructions.

## 📊 Success Metrics

- **Time Savings**: 25+ minutes per proposal (target: 30 min → 2 min)
- **Proposal Quality**: 95%+ accuracy in formatting and completeness
- **RAG Relevance**: 80%+ of proposals cite relevant past projects
- **Win Rate**: 20% increase in proposal acceptance (tracked)
- **User Activation**: 70% of signups generate first proposal within 24h

## 🛠️ Tech Stack

**Frontend**:

- Next.js 15.3.5
- React 19
- TypeScript 5.x
- TailwindCSS 4
- shadcn/ui
- TanStack Query 5.x
- Supabase JS Client

**Backend**:

- Python 3.11+
- FastAPI 0.104+
- ChromaDB 0.4+
- LangChain 0.1+
- OpenAI GPT-4-turbo
- Crawlee
- pypdf, python-docx

**Infrastructure**:

- PostgreSQL (Supabase)
- ChromaDB (self-hosted)
- Vercel (frontend)
- Railway (backend)

## 🤝 Contributing

See [CONTRIBUTING.md](./docs/CONTRIBUTING.md) for development workflow and coding standards.

## 📄 License

[MIT License](./LICENSE)

## 🔗 Links

- [Documentation](./docs/)
- [API Contracts](./specs/001-ai-auto-bidder-platform/contracts/)
- [Feature Specification](./specs/001-ai-auto-bidder-platform/spec.md)
- [Implementation Plan](./specs/001-ai-auto-bidder-platform/plan.md)

---

**Built with ❤️ by the Auto Bidder Team**
