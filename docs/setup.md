# Setup Guide

**Purpose:** Get the Auto-Bidder platform running from zero to development.  
Covers local dev setup, authentication, ChromaDB, and production deployment to Railway.

---

## Prerequisites

- Node.js 20+
- Python 3.11+ (3.12+ recommended)
- Docker & Docker Compose
- DeepSeek or OpenAI API key (for LLM)
- `make` (available on macOS via Xcode CLI tools)

> 💡 This project has a `Makefile` at the root with shortcuts for all common commands.
> Run `make help` or see [makefile-commands.md](makefile-commands.md) for the full reference.

---

## Quick Start (Local Dev)

### Step 1: Infrastructure

```bash
make infra-up         # Start PostgreSQL + ChromaDB
make db-migrate       # Apply all pending migrations
```

Or manually:
```bash
docker-compose up -d
python backend/scripts/run_migrations.py
```

### Step 2: Environment

**Frontend** (`frontend/.env.local`):
```bash
NEXT_PUBLIC_BACKEND_API_URL=http://localhost:5555
PYTHON_AI_SERVICE_URL=http://localhost:5555
```

**Backend** (`backend/.env`):
```bash
DATABASE_URL=postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/auto_bidder_dev
JWT_SECRET=<generate with: openssl rand -hex 32>
JWT_ALGORITHM=HS256
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-your-key
CHROMA_PERSIST_DIR=./chroma_db
```

### Step 3: Start Application

```bash
make install          # Install all dependencies (one-time)
make dev              # Start both servers concurrently
```

Or individually:
```bash
make backend-dev      # Backend on :5555
make frontend-dev     # Frontend on :5556
```

### Step 4: Verify

1. Backend: [http://localhost:5555/health](http://localhost:5555/health) → `{"status":"healthy"}`
2. API docs: [http://localhost:5555/docs](http://localhost:5555/docs)
3. Frontend: [http://localhost:5556](http://localhost:5556) → Sign up → Dashboard

### Troubleshooting

| Issue | Solution |
|-------|----------|
| "Failed to create database pool" | `docker-compose ps` — ensure PostgreSQL is running |
| "JWT_SECRET not found" | Add `JWT_SECRET` to `backend/.env` |
| "Network Error" / "Failed to fetch" | Check `NEXT_PUBLIC_BACKEND_API_URL` in `frontend/.env.local` |
| "Unauthorized" after login | Clear localStorage and login again |
| Port conflicts | `lsof -ti:5556 \| xargs kill -9` (or 5555) |
| Backend import errors | Activate venv, run `pip install -r requirements.txt` |

---

## Authentication

The platform uses **custom JWT authentication**:
- Custom `users` table in PostgreSQL
- JWT issued by FastAPI at `POST /api/auth/login`
- Frontend stores token in localStorage; sends `Authorization: Bearer <token>`

### Test via API

```bash
# Signup
curl -X POST http://localhost:5555/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","full_name":"Test User"}'

# Login
curl -X POST http://localhost:5555/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Get current user (use token from login)
curl -X GET http://localhost:5555/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### JWT Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `JWT_SECRET` | — | Secret for signing tokens (generate with `openssl rand -hex 32`) |
| `JWT_ALGORITHM` | HS256 | Signing algorithm |
| `JWT_EXPIRATION_MINUTES` | 10080 | Token expiry (7 days) |

### Common Auth Issues

| Issue | Solution |
|-------|----------|
| "Failed to create database pool" | Ensure PostgreSQL running (`docker-compose ps`) |
| "JWT_SECRET not found" | Add to `backend/.env` |
| "Network Error" | Backend running? Check `NEXT_PUBLIC_BACKEND_API_URL` |
| "Unauthorized" after login | Clear localStorage and login again |

---

## ChromaDB — Vector Store for RAG

ChromaDB stores document embeddings for Knowledge Base RAG (proposal generation).

### Modes

| Mode | Config | Use Case |
|------|--------|----------|
| **Local** | `CHROMA_PERSIST_DIR=./chroma_db`, no `CHROMA_HOST` | Development |
| **Docker** | `CHROMA_HOST=localhost`, `CHROMA_PORT=8001` | Production, teams |

**Logic:** `CHROMA_HOST` wins. If set → HTTP client; else → PersistentClient. Falls back to local if Docker fails.

### Quick Config

**Local (dev):** Unset/comment `CHROMA_HOST`. Data in `backend/chroma_db/`.

**Docker:** `docker-compose up -d chromadb`. Set `CHROMA_HOST=localhost` and `CHROMA_PORT=8001` in `.env`.

### Upgrade to Docker

1. `pip install --upgrade chromadb` (v0.5+ for Docker v2 API)
2. Set `CHROMA_HOST=localhost`, `CHROMA_PORT=8001`
3. Restart backend

### Troubleshooting

- **Connection refused:** Ensure Docker ChromaDB is running (`docker ps | grep chromadb`)
- **v1 API deprecated:** Upgrade client to chromadb>=0.5
- **Data after switch:** Local and Docker use separate storage; migrate if needed

---

## Railway Deployment

Complete guide to deploy the backend and databases to Railway.

### Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **Railway CLI** (optional):
   ```bash
   npm install -g @railway/cli
   ```
3. **GitHub Repository**: Code pushed to GitHub

### Step-by-Step

#### 1. Create Project

**CLI:** `railway login && railway init`  
**Dashboard:** Go to [railway.app/new](https://railway.app/new) → "Deploy from GitHub repo" → select your repo.

#### 2. Add PostgreSQL

Click **"+ New"** → **"Database"** → **"PostgreSQL"**. Railway auto-provides `DATABASE_URL`.

#### 3. Add ChromaDB

Click **"+ New"** → **"Empty Service"** → name it `chromadb` → Docker image: `chromadb/chroma:latest`.

Set env vars:
```
IS_PERSISTENT=TRUE
ANONYMIZED_TELEMETRY=FALSE
```

In **Settings → Networking**, click **"Generate Domain"** — note the internal URL: `chromadb.railway.internal:8000`.

#### 4. Deploy FastAPI Backend

Click **"+ New"** → **"GitHub Repo"** → select repo. Railway auto-detects `railway.toml`.

Settings → Build:
- Build method: `Dockerfile`
- Dockerfile path: `backend/Dockerfile`
- Build context: `backend`

#### 5. Environment Variables

Set these in the FastAPI service **Variables**:

```bash
DATABASE_URL=${{Postgres.DATABASE_URL}}
CHROMA_HOST=chromadb.railway.internal
CHROMA_PORT=8000
JWT_SECRET=<generate secure random>
OPENAI_API_KEY=<key>     # or DEEPSEEK_API_KEY
LLM_PROVIDER=deepseek
RESEND_API_KEY=<key>     # for email features
ENVIRONMENT=production
LOG_LEVEL=INFO
CORS_ORIGINS=https://your-frontend.vercel.app
```

Optional:
```bash
AUTO_DISCOVERY_ENABLED=true
ETL_USE_PERSISTENCE=true
PROJECT_FILTER_KEYWORDS=python,fastapi,react
```

#### 6. Database Migrations

```bash
# Via Railway CLI
railway connect Postgres
\i database/migrations/001_initial_schema.sql
\q

# Or run migration script
railway run python backend/scripts/run_migrations.py
```

#### 7. Generate Public URL

**Settings → Networking → Generate Domain**. Test: `https://your-domain.up.railway.app/health`.

#### 8. Connect Frontend

Update frontend env vars (Vercel or `.env.local`):
```bash
NEXT_PUBLIC_API_URL=https://your-backend.up.railway.app
PYTHON_AI_SERVICE_URL=https://your-backend.up.railway.app
```

### Railway Commands

```bash
railway login          # Login
railway link           # Link to project
railway logs           # View logs
railway up             # Deploy
railway variables      # Get env vars
railway connect Postgres  # DB shell
railway run <cmd>     # Run in context
```

### Cost Estimation

| Service | Hobby ($5/mo) | Pro ($20/mo) |
|---------|:-------------:|:------------:|
| FastAPI Backend | $3-8 | Included in credits |
| PostgreSQL | $2-5 | Included |
| ChromaDB | $3-8 | Included |
| **Total** | **~$8-21/mo** | **~$20+/mo** |

### Troubleshooting

| Issue | Solution |
|-------|----------|
| Service won't start | Check logs (`railway logs`), verify env vars, test Dockerfile locally |
| DB connection failed | Verify `DATABASE_URL`, check PostgreSQL service, run migrations |
| ChromaDB timeout | Use internal URL `chromadb.railway.internal:8000`, check CHROMA_HOST/PORT |
| High costs | Enable sleep mode, optimize Docker image, scale down resources |

### Deployment Checklist

- [ ] Railway account created
- [ ] GitHub repository connected
- [ ] PostgreSQL database added
- [ ] ChromaDB service configured
- [ ] FastAPI service deployed
- [ ] All environment variables set
- [ ] Database migrations run
- [ ] Health check endpoint responding
- [ ] Public domain generated
- [ ] Frontend connected to backend API
- [ ] CORS configured correctly
- [ ] Logs verified (no errors)
