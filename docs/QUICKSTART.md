# 🚀 Quick Start Guide

**Get your Auto-Bidder platform running in 10 minutes**

---

## Prerequisites

Before starting, ensure you have:

- ✅ Node.js 20+ installed (`node --version`)
- ✅ Python 3.11+ installed (`python --version`)
- ✅ Git installed
- ⏳ Supabase CLI (`brew install supabase/tap/supabase`)
- ⏳ Supabase account (https://supabase.com - free tier OK)
- ⏳ OpenAI API key (https://platform.openai.com)

---

## Step 1: Get API Credentials (5 minutes)

### Supabase Setup

1. Go to https://supabase.com and create a free account
2. Create a new project (choose a region close to you)
3. Wait ~2 minutes for project to provision
4. Go to **Settings** → **API**
5. Copy these values:
   - `Project URL` (looks like `https://xxxxx.supabase.co`)
   - `anon/public` key (starts with `eyJ...`)
   - `service_role` key (starts with `eyJ...` - keep this secret!)

### OpenAI Setup

1. Go to https://platform.openai.com/api-keys
2. Click **Create new secret key**
3. Copy the key (starts with `sk-...`)
4. Add $5-10 credit if needed

---

## Step 2: Configure Environment (2 minutes)

### Frontend Environment

```bash
cd auto-bidder/frontend
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

## Step 3: Start the Stack (10 minutes)

### Terminal 1: Database

```bash
cd auto-bidder

# Initialize Supabase (first time only)
supabase init

# Start local Supabase (PostgreSQL + Studio)
supabase start

# Apply migrations + seed data
supabase db reset

# ✅ Success: You should see "Database reset complete"
# Visit http://localhost:54323 to see Supabase Studio
```

### Terminal 2: Backend (Python)

```bash
cd auto-bidder/backend

# Create virtual environment (first time only)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies (first time only, ~5 minutes)
pip install -r requirements.txt

# Start FastAPI server
uvicorn app.main:app --reload --port 8000

# ✅ Success: You should see "Application startup complete"
# Visit http://localhost:8000/docs for API documentation
```

### Terminal 3: Frontend (Next.js)

```bash
cd auto-bidder/frontend

# Install dependencies (first time only, ~3 minutes)
npm install

# Start development server
npm run dev

# ✅ Success: You should see "Ready on http://localhost:3000"
# Visit http://localhost:3000 to see the landing page
```

---

## Step 4: Test the Platform (3 minutes)

### 1. Test Backend Health

```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy","version":"0.1.0",...}

curl http://localhost:8000/health/dependencies
# Should show OpenAI, Supabase, and ChromaDB status
```

### 2. Test Frontend

Open http://localhost:3000 in your browser
- ✅ Should see landing page with "Auto Bidder" title
- ✅ Click "Get Started" → Should go to signup page

### 3. Create Test Account

1. Go to http://localhost:3000/signup
2. Enter email: `test@example.com`
3. Enter password: `password123` (min 8 chars)
4. Click "Create account"
5. ✅ Should redirect to dashboard

### 4. Verify Database

1. Go to http://localhost:54323 (Supabase Studio)
2. Go to **Table Editor** → `user_profiles`
3. ✅ Should see your test user
4. Go to **Table Editor** → `projects`
5. ✅ Should see 10 seed projects

---

## Step 5: Install UI Components (Optional, 2 minutes)

```bash
cd auto-bidder/frontend

# Install shadcn/ui components
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add input
npx shadcn-ui@latest add select
npx shadcn-ui@latest add table
npx shadcn-ui@latest add toast

# ✅ Success: Components installed in src/components/ui/
```

---

## ✅ Success Checklist

After completing the quick start, verify:

- [ ] Backend runs at http://localhost:8000
- [ ] Backend health check returns `{"status":"healthy"}`
- [ ] Frontend runs at http://localhost:3000
- [ ] Supabase Studio accessible at http://localhost:54323
- [ ] Can create account and login
- [ ] Dashboard loads after login
- [ ] Seed data visible in database

---

## 🐛 Troubleshooting

### Frontend won't start

```bash
# Clear cache and reinstall
cd frontend
rm -rf node_modules .next
npm install
npm run dev
```

### Backend import errors

```bash
# Make sure virtual environment is activated
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Database connection failed

```bash
# Restart Supabase
supabase stop
supabase start

# Verify it's running
supabase status
```

### Port already in use

```bash
# Kill process using port 3000 (frontend)
lsof -ti:3000 | xargs kill -9

# Kill process using port 8000 (backend)
lsof -ti:8000 | xargs kill -9

# Kill process using port 54323 (Supabase)
supabase stop
```

---

## 📖 Next Steps

Now that your stack is running:

1. **Read the docs**: Check `auto-bidder/docs/START_HERE.md`
2. **Explore the code**: Review `SESSION_SUMMARY.md` for what's been built
3. **Start developing**: Begin with Phase 3 (User Story 1 - Job Discovery)
4. **Join the journey**: Follow `specs/001-ai-auto-bidder-platform/tasks.md`

---

## 🔗 Important URLs

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | Next.js app |
| Backend API | http://localhost:8000 | FastAPI service |
| API Docs | http://localhost:8000/docs | Swagger UI |
| Health Check | http://localhost:8000/health | Service status |
| Supabase Studio | http://localhost:54323 | Database UI |
| ChromaDB | `./backend/chroma_db/` | Local vector store |

---

## 💬 Need Help?

- 📚 Check `README.md` for project overview
- 📊 Check `IMPLEMENTATION_STATUS.md` for current progress
- 📝 Check `SESSION_SUMMARY.md` for detailed implementation notes
- 🎯 Check `specs/001-ai-auto-bidder-platform/` for feature specs

---

**Setup Time**: ~10 minutes (excluding dependency installations)  
**Total Install Time**: ~20-25 minutes (with npm/pip installs)  
**Ready to Code**: ✅ Foundational infrastructure complete!
