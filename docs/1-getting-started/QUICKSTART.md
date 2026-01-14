# 🚀 Quick Start Guide

**Get your Auto-Bidder platform running in 10 minutes**

---

## 📋 Prerequisites

Before starting, ensure you have:

- ✅ **Node.js 20+** installed (`node --version`)
- ✅ **Python 3.11+** (3.12+ recommended) installed (`python --version`)
- ✅ **Docker & Docker Compose** installed
- ✅ **Git** installed
- ⏳ **Supabase CLI** (`brew install supabase/tap/supabase`)
- ⏳ **Supabase account** ([supabase.com](https://supabase.com))
- ⏳ **OpenAI API key** ([platform.openai.com](https://platform.openai.com))

---

## 🛠️ Step 1: Infrastructure Setup

### 1. Start PostgreSQL

We use Docker for local database and vector storage.

```bash
docker compose up -d postgres chromadb
```

### 2. Get API Credentials

- **Supabase**: Create a new project, go to **Settings** → **API**, and copy the `Project URL`, `anon/public` key, and `service_role` key.
- **OpenAI**: Create a new secret key at [platform.openai.com/api-keys](https://platform.openai.com/api-keys).

---

## ⚙️ Step 2: Configure Environment

### Frontend Environment

```bash
cd frontend
cp .env.example .env.local
```

Edit `.env.local`:

```bash
NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJxxxxxxxxxxxx
PYTHON_AI_SERVICE_URL=http://localhost:8000
```

### Backend Environment

```bash
cd ../backend
cp .env.example .env
```

Edit `.env`:

```bash
OPENAI_API_KEY=sk-xxxxxxxxxxxx
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_KEY=eyJxxxxxxxxxxxx
CHROMA_PERSIST_DIR=./chroma_db
```

---

## 🏃 Step 3: Start the Application

### Terminal 1: Database Migrations

```bash
cd ..
# Initialize Supabase (first time only)
supabase init
supabase start

# Apply migrations
supabase db reset
```

### Terminal 2: Backend (Python)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Terminal 3: Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```

---

## ✅ Step 4: Verify Installation

1. **Backend Health**: Visit [http://localhost:8000/health](http://localhost:8000/health). Should see `{"status":"healthy"}`.
2. **API Docs**: Visit [http://localhost:8000/docs](http://localhost:8000/docs) for Swagger UI.
3. **Frontend Dashboard**: Visit [http://localhost:3000](http://localhost:3000). Create an account at `/signup`.
4. **Supabase Studio**: Visit [http://localhost:54323](http://localhost:54323) to inspect tables.

---

## 🧪 Core Features to Test

### 1. Navigation Context Preservation

Apply a filter on the Projects page, navigate away, and return. The filter and scroll position should be preserved.

### 2. Auto-Save & Recovery

Start drafting a proposal. Wait 10 seconds for the "Saved" indicator. Reload the page to see the recovery prompt.

### 3. Performance Analytics

Visit `/analytics` to see navigation timing metrics (target: <500ms).

---

## 🐛 Troubleshooting

- **Backend import errors**: Ensure your virtual environment is active and `pip install -r requirements.txt` was successful.
- **Port conflicts**: If port 3000 or 8000 is used, kill the process using `lsof -ti:PORT | xargs kill -9`.
- **Database connection**: Ensure Docker containers are running (`docker ps`).

---

**Ready to Build?** Check [ARCHITECTURE_DIAGRAM.md](../2-architecture/ARCHITECTURE_DIAGRAM.md) for a deep dive into how the system works.
