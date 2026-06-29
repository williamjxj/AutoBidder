# Setup and Run

**Purpose:** Get the Auto-Bidder platform running in ~10 minutes.

---

## Prerequisites

- Node.js 20+
- Python 3.11+ (3.12+ recommended)
- Docker & Docker Compose
- DeepSeek or OpenAI API key (for LLM)
- `make` (available on macOS via Xcode CLI tools)

> 💡 **Tip:** This project has a `Makefile` at the root with shortcuts for all common commands.
> Run `make help` to see them, or refer to [docs/makefile-commands.md](makefile-commands.md) for the full reference.

---

## Step 1: Infrastructure

**Recommended — using Makefile:**
```bash
cd auto-bidder
make infra-up         # Start PostgreSQL + ChromaDB
make db-migrate       # Apply all pending migrations
```

**Or manually:**
```bash
cd auto-bidder
docker-compose up -d
# Apply migrations via psql
docker exec -i auto-bidder-postgres psql -U postgres -d auto_bidder_dev -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"; CREATE EXTENSION IF NOT EXISTS \"pg_trgm\";"
docker exec -i auto-bidder-postgres psql -U postgres -d auto_bidder_dev < database/migrations/001_initial_schema.sql
docker exec -i auto-bidder-postgres psql -U postgres -d auto_bidder_dev < database/migrations/016_remove_scoring_artifacts.sql

# Or run all migrations in order (requires DATABASE_URL):
python backend/scripts/run_migrations.py
```

---

## Step 2: Environment

**Frontend** (`frontend/.env.local`):
```bash
NEXT_PUBLIC_BACKEND_API_URL=http://localhost:5555
PYTHON_AI_SERVICE_URL=http://localhost:5555
```

**Backend** (`backend/.env`):
```bash
DATABASE_URL=postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/auto_bidder_dev
JWT_SECRET=your-super-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=10080
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-your-key
CHROMA_PERSIST_DIR=./chroma_db
```

---

## Step 3: Start Application

**Recommended — using Makefile (single command):**
```bash
cd auto-bidder
make install    # Install all dependencies (one-time)
make dev        # Start both servers concurrently
```

**Or run servers individually:**
```bash
# Terminal 1 — Backend:
cd auto-bidder
make backend-dev

# Terminal 2 — Frontend:
cd auto-bidder
make frontend-dev
```

**Or manually:**
```bash
# Terminal 1 — Backend:
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 5555

# Terminal 2 — Frontend:
cd frontend
npm install
npm run dev
```

---

## Step 4: Verify

1. Backend: [http://localhost:5555/health](http://localhost:5555/health) → `{"status":"healthy"}`
2. API docs: [http://localhost:5555/docs](http://localhost:5555/docs)
3. Frontend: [http://localhost:5556](http://localhost:5556) → Sign up → Dashboard

---

## User Workflow (After Setup)

1. **Knowledge Base** — Upload portfolio PDFs/DOCX for RAG context
2. **Strategies** — Create proposal tone (professional, casual, technical)
3. **Projects** → Discover Jobs → Generate Proposal on a job card → AI draft

See [proposals.md](proposals.md) for the full flow.

---

## Troubleshooting

- **Backend import errors:** Activate venv, run `pip install -r requirements.txt`
- **Port conflicts:** `lsof -ti:5556 | xargs kill -9` (or 5555)
- **Database:** Ensure `docker ps` shows postgres and chromadb

---

**Next:** [user-guides.md](user-guides.md) for UI usage | [diagrams/architecture-diagram.md](diagrams/architecture-diagram.md) for architecture
