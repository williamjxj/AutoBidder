# Developer Quickstart: Workflow Optimization

**Feature**: 001-smooth-workflow  
**Estimated Setup Time**: 30 minutes  
**Prerequisites**: Docker, Node.js 18+, Python 3.12+, Git

## Overview

This guide helps developers set up the Workflow Optimization feature for local development. Follow these steps in order.

---

## Step 1: Environment Setup

### 1.1 Pull Latest Code

```bash
cd ./auto-bidder
git checkout 001-smooth-workflow
git pull origin 001-smooth-workflow
```

### 1.2 Update Environment Variables

**Backend** (`backend/.env`):

```bash
cd backend
cp .env .env.backup  # Backup existing .env

# Add new variables to backend/.env
cat >> .env << 'EOF'

# Workflow Optimization Settings
SESSION_STATE_TTL_HOURS=24
DRAFT_RETENTION_HOURS=24
MAX_DRAFT_SIZE_KB=1000
ENABLE_WORKFLOW_ANALYTICS=true
EOF
```

**Frontend** (`frontend/.env.local`):

```bash
cd ../frontend
cp .env.local .env.local.backup  # Backup existing

# Add new variables to frontend/.env.local
cat >> .env.local << 'EOF'

# Workflow Optimization Settings
NEXT_PUBLIC_BACKEND_API_URL=http://localhost:8000
NEXT_PUBLIC_AUTO_SAVE_INTERVAL_MS=10000
NEXT_PUBLIC_OFFLINE_SYNC_RETRY_MS=5000
NEXT_PUBLIC_ENABLE_KEYBOARD_SHORTCUTS=true
NEXT_PUBLIC_VIRTUAL_SCROLL_THRESHOLD=100
EOF
```

---

## Step 2: Database Migration

### 2.1 Start PostgreSQL

```bash
cd ..  # Return to repo root
docker-compose up -d postgres
```

Wait 5-10 seconds for PostgreSQL to initialize.

### 2.2 Apply Migration

```bash
# Option A: Using psql directly
docker exec -i auto-bidder-postgres psql -U postgres -d auto_bidder_dev < database/migrations/004_workflow_optimization.sql

# Option B: Using Supabase CLI (if available)
supabase db push --include-all

# Verify migration
docker exec -it auto-bidder-postgres psql -U postgres -d auto_bidder_dev -c "\dt" | grep -E "(session_states|draft_work|workflow_analytics)"
```

**Expected Output**:
```
 public | draft_work             | table | postgres
 public | user_session_states    | table | postgres
 public | workflow_analytics     | table | postgres
```

---

## Step 3: Backend Setup

### 3.1 Install Dependencies

```bash
cd backend

# Activate virtual environment (if not already active)
source venv/bin/activate

# Install dependencies (should already have core deps)
pip install -r requirements.txt

# Verify installation
python -c "import fastapi; import pydantic; print('Backend dependencies OK')"
```

### 3.2 Run Backend Server

```bash
# Start backend (with auto-reload)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Expected Output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReloader
INFO:     Started server process [12346]
INFO:     🚀 Auto-Bidder AI Service starting...
INFO:     Environment: development
```

### 3.3 Verify Backend APIs

Open new terminal:

```bash
# Health check
curl http://localhost:8000/health

# API docs (OpenAPI)
open http://localhost:8000/docs

# Verify workflow endpoints appear in docs:
# - /api/session/state
# - /api/drafts
# - /api/sync/batch
```

---

## Step 4: Frontend Setup

### 4.1 Install Dependencies

```bash
cd ../frontend  # From repo root

# Install dependencies (includes new packages)
npm install

# Verify new packages installed
npm list idb react-window | grep -E "(idb|react-window)"
```

**Expected Output**:
```
├── idb@8.0.0
├── react-window@1.8.10
```

### 4.2 Run Frontend Server

```bash
# Start Next.js dev server
npm run dev
```

**Expected Output**:
```
  ▲ Next.js 15.3.5
  - Local:        http://localhost:3000
  - Ready in 2.5s
```

### 4.3 Verify Frontend

1. Open http://localhost:3000
2. Login with test account
3. Navigate to /dashboard/projects
4. Open browser DevTools → Console
5. Look for workflow-related logs (if implemented):
   - "Session state loaded"
   - "Auto-save initialized"

---

## Step 5: Feature Verification

### 5.1 Test Session State

**Manual Test**:
1. Navigate to /dashboard/projects
2. Apply some filters (e.g., search "design")
3. Navigate to /dashboard/proposals
4. Use browser back button
5. **Expected**: Filters are preserved when returning to projects

**Check localStorage**:
```javascript
// In browser console
localStorage.getItem('workflow_session_state')
// Should show JSON with active_feature, context_data
```

### 5.2 Test Auto-Save

**Manual Test** (once implemented):
1. Navigate to /dashboard/proposals/new
2. Start filling out form
3. Wait 10 seconds without clicking Save
4. Check Network tab for POST `/api/drafts/proposal/new`
5. **Expected**: Auto-save request sent

**Verify in database**:
```bash
# Query drafts table
docker exec -it auto-bidder-postgres psql -U postgres -d auto_bidder_dev \
  -c "SELECT entity_type, auto_save_count, created_at FROM draft_work LIMIT 5;"
```

### 5.3 Test Offline Mode

**Manual Test** (once implemented):
1. Open DevTools → Network tab
2. Check "Offline" checkbox
3. Make a change (e.g., update project name)
4. **Expected**: Change queued, offline banner appears
5. Uncheck "Offline"
6. **Expected**: "Syncing changes..." toast, change syncs

**Check IndexedDB**:
```javascript
// In browser console
indexedDB.databases().then(dbs => console.log(dbs))
// Should show 'workflow_db' or similar
```

### 5.4 Test Keyboard Shortcuts

**Manual Test**:
1. Press `Cmd/Ctrl + K`
2. **Expected**: Search modal opens
3. Press `Cmd/Ctrl + N`
4. **Expected**: Navigate to new proposal page
5. Press `Cmd/Ctrl + S` while editing
6. **Expected**: Manual save triggered

---

## Step 6: Run Tests

### 6.1 Backend Tests

```bash
cd backend

# Run unit tests
pytest tests/unit/test_session_manager.py -v
pytest tests/unit/test_draft_manager.py -v
pytest tests/unit/test_conflict_resolver.py -v

# Run integration tests
pytest tests/integration/test_workflow_api.py -v

# Run all tests with coverage
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html
```

### 6.2 Frontend Tests

```bash
cd ../frontend

# Run unit tests
npm run test

# Run E2E tests (once implemented)
npx playwright test tests/e2e/workflow

# Run specific test file
npm run test -- auto-save.test.ts
```

---

## Step 7: Development Workflow

### 7.1 Hot Reload

Both backend and frontend support hot reload:

- **Backend**: uvicorn `--reload` flag watches `app/` directory
- **Frontend**: Next.js watches `src/` directory

Make code changes and see updates immediately without restart.

### 7.2 Database Changes

If you modify database schema:

```bash
# Create new migration file
cd database/migrations
touch 005_my_changes.sql

# Apply migration
docker exec -i auto-bidder-postgres psql -U postgres -d auto_bidder_dev < database/migrations/005_my_changes.sql

# If you need to rollback
docker-compose down -v postgres  # Warning: deletes data!
docker-compose up -d postgres
# Re-apply all migrations in order
```

### 7.3 Debugging

**Backend Debugging**:
```bash
# Enable debug logging
# In backend/.env, set:
LOG_LEVEL=DEBUG

# Restart backend to see detailed logs
```

**Frontend Debugging**:
```javascript
// Add to any component
console.log('Session state:', useSessionState())
console.log('Draft manager:', useDraftManager())

// Or use React DevTools extension
```

### 7.4 API Testing

**Using curl**:
```bash
# Get JWT token (after login)
TOKEN="your-supabase-jwt-token"

# Test session state API
curl -X GET http://localhost:8000/api/session/state \
  -H "Authorization: Bearer $TOKEN"

# Test draft API
curl -X PUT http://localhost:8000/api/drafts/proposal/new \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"draft_data": {"title": "Test"}}'
```

**Using Postman/Insomnia**:
1. Import OpenAPI specs from `specs/001-smooth-workflow/contracts/`
2. Set environment variable `baseUrl` = `http://localhost:8000/api`
3. Set authorization header with Supabase JWT token
4. Test all endpoints

---

## Troubleshooting

### Issue: PostgreSQL Connection Error

**Symptoms**: `Connection refused` or `could not connect to server`

**Solution**:
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# If not running, start it
docker-compose up -d postgres

# Check logs
docker logs auto-bidder-postgres

# Verify port 5432 is accessible
nc -zv localhost 5432
```

### Issue: Migration Already Applied

**Symptoms**: `ERROR: relation "user_session_states" already exists`

**Solution**:
```bash
# Check what tables exist
docker exec -it auto-bidder-postgres psql -U postgres -d auto_bidder_dev -c "\dt"

# If tables exist, migration is already applied (no action needed)
# If you need to reset (WARNING: deletes all data):
docker-compose down -v postgres
docker-compose up -d postgres
# Re-apply migrations 001, 002, 003, 004 in order
```

### Issue: Frontend Build Errors

**Symptoms**: `Module not found: Can't resolve '@/lib/workflow/...'`

**Solution**:
```bash
# Ensure all files created
ls -la src/lib/workflow/

# If missing, create placeholder files:
mkdir -p src/lib/workflow
touch src/lib/workflow/session-context.tsx
touch src/lib/workflow/draft-manager.ts
# ... etc

# Restart Next.js dev server
npm run dev
```

### Issue: Auto-Save Not Working

**Symptoms**: No auto-save requests in Network tab

**Checklist**:
1. ✅ Migration applied? Check `draft_work` table exists
2. ✅ Backend running? Visit http://localhost:8000/docs
3. ✅ Frontend env var set? Check `NEXT_PUBLIC_AUTO_SAVE_INTERVAL_MS` in `.env.local`
4. ✅ User authenticated? Check `localStorage.getItem('supabase.auth.token')`
5. ✅ Hook implemented? Check if `useAutoSave` hook is called in form component

### Issue: Keyboard Shortcuts Not Working

**Symptoms**: `Cmd/Ctrl + K` does nothing

**Checklist**:
1. ✅ Env var enabled? Check `NEXT_PUBLIC_ENABLE_KEYBOARD_SHORTCUTS=true`
2. ✅ Hook attached? Verify `useKeyboardShortcuts()` called in layout
3. ✅ Check browser console for errors
4. ✅ Try in different browser (some extensions interfere)

---

## Next Steps

1. ✅ **Environment Setup Complete**
2. ⏭️ **Read Implementation Tasks**: See `tasks.md` (created by `/speckit.tasks`)
3. ⏭️ **Pick a Task**: Start with P1 tasks (backend foundation, frontend hooks)
4. ⏭️ **Test as You Go**: Run tests after each task
5. ⏭️ **Review Spec**: Reference `spec.md` for requirements
6. ⏭️ **Review Plan**: Reference `plan.md` for architecture decisions

---

## Useful Commands Reference

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker logs -f auto-bidder-backend
docker logs -f auto-bidder-postgres

# Database shell
docker exec -it auto-bidder-postgres psql -U postgres -d auto_bidder_dev

# Backend shell
cd backend && source venv/bin/activate

# Frontend shell
cd frontend

# Run all tests
cd backend && pytest && cd ../frontend && npm test

# Clean restart (WARNING: deletes data)
docker-compose down -v
docker-compose up -d
```

---

## Resources

- **Spec**: [spec.md](./spec.md) - Feature requirements
- **Plan**: [plan.md](./plan.md) - Technical architecture
- **Research**: [research.md](./research.md) - Technology decisions
- **Data Model**: [data-model.md](./data-model.md) - Database schemas
- **API Contracts**: [contracts/](./contracts/) - OpenAPI specs
- **Clarifications**: [../../docs/001-workflow-clarifications.md](../../docs/001-workflow-clarifications.md) - Environment Q/A

---

**Setup Status**: ✅ Complete  
**Ready to Code**: 🚀 Yes  
**Need Help?**: Check troubleshooting section above or ask the team
