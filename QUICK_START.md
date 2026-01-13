# Quick Start Guide - Workflow Optimization Feature

Get up and running in 5 minutes! ⚡

---

## 🚀 Prerequisites

- Docker & Docker Compose installed
- Node.js 18+ installed
- Python 3.12+ installed

---

## 📦 Setup (First Time)

### 1. Start PostgreSQL

```bash
cd /Users/william.jiang/my-experiments/bidding/auto-bidder
docker compose up -d postgres
```

### 2. Apply Database Migrations

```bash
# Apply local auth setup (required for local dev)
docker exec -i auto-bidder-postgres psql -U postgres -d auto_bidder_dev < database/migrations/000_local_auth_setup.sql

# Apply workflow optimization migration
docker exec -i auto-bidder-postgres psql -U postgres -d auto_bidder_dev < database/migrations/004_workflow_optimization.sql
```

### 3. Verify Database Tables

```bash
docker exec -i auto-bidder-postgres psql -U postgres -d auto_bidder_dev -c "\dt" | grep -E "(user_session_states|draft_work|workflow_analytics)"
```

Expected output:
```
 public | draft_work            | table | postgres
 public | user_session_states   | table | postgres
 public | workflow_analytics    | table | postgres
```

---

## 🏃 Run the Application

### Terminal 1: Backend

```bash
cd backend

# Activate virtual environment (if using venv)
source venv/bin/activate
# OR if using conda/other env manager, activate your environment

# Install dependencies (if first time)
pip install -r requirements.txt

# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected**: Server running at `http://localhost:8000`

### Terminal 2: Frontend

```bash
cd frontend

# Install dependencies (if first time)
npm install

# Start Next.js dev server
npm run dev
```

**Expected**: App running at `http://localhost:3000`

---

## ✅ Verify Installation

### 1. Check Backend Health

Open: `http://localhost:8000/health`

**Expected Response**:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-12T..."
}
```

### 2. Check API Documentation

Open: `http://localhost:8000/docs`

**Expected**: FastAPI Swagger UI showing:
- Session state endpoints
- Draft management endpoints
- Analytics endpoints

### 3. Check Frontend

Open: `http://localhost:3000`

**Expected**: Auto-Bidder dashboard

---

## 🧪 Test Core Features

### Test 1: Navigation with Context Preservation ⏱️ <500ms

1. Navigate to **Projects** (`/projects`)
2. Apply a filter (select a status)
3. Scroll down the page
4. Navigate to **Proposals** (`/proposals`)
5. Click **browser back button**
6. ✅ **Verify**: Projects page shows with filter and scroll position restored

### Test 2: Auto-Save System 💾

1. Navigate to **New Proposal** (`/proposals/new`)
2. Start typing in the form fields
3. Wait 10 seconds
4. ✅ **Verify**: See "Saved" indicator in top right
5. Close the browser tab
6. Reopen `/proposals/new`
7. ✅ **Verify**: See yellow recovery banner
8. Click "Recover Draft"
9. ✅ **Verify**: Form fields populated with your data

### Test 3: Conflict Detection ⚠️

1. Open `/proposals/new` in **two separate browser tabs**
2. **Tab 1**: Type "First version" in title, wait for save
3. **Tab 2**: Type "Second version" in title, wait for save
4. ✅ **Verify**: Conflict dialog appears in Tab 2
5. Choose "Keep Your Changes"
6. ✅ **Verify**: "Second version" is saved

### Test 4: Performance Monitoring 📊

1. Navigate between pages: Projects → Proposals → Analytics
2. Go to **Analytics** page (`/analytics`)
3. Scroll down to "Workflow Performance (Current Session)"
4. ✅ **Verify**: See metrics:
   - Total Navigations count
   - Average Duration (should be <500ms)
   - Recent Navigation Times list

### Test 5: Error Handling ⚠️

1. **Stop the backend server** (Ctrl+C in Terminal 1)
2. In the frontend, try to interact with auto-save
3. ✅ **Verify**: Error toast appears with:
   - Clear error message
   - Explanation of what went wrong
   - Steps to fix
4. **Restart the backend server**
5. ✅ **Verify**: Connection restored, auto-save resumes

---

## 🎯 What's Working

| Feature | Status | Test |
|---------|--------|------|
| Navigation Context | ✅ | Test 1 |
| Auto-Save | ✅ | Test 2 |
| Draft Recovery | ✅ | Test 2 |
| Conflict Detection | ✅ | Test 3 |
| Performance Tracking | ✅ | Test 4 |
| Error Handling | ✅ | Test 5 |
| Online/Offline Status | ✅ | Sidebar indicator |
| Browser Back/Forward | ✅ | Test 1 |
| Session State Sync | ✅ | Multi-tab same state |

---

## 🐛 Troubleshooting

### Backend won't start

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Fix**:
```bash
cd backend
pip install -r requirements.txt
```

---

### Frontend won't start

**Error**: `Cannot find module 'next'`

**Fix**:
```bash
cd frontend
npm install
```

---

### Database connection error

**Error**: `connection refused` or `database does not exist`

**Fix**:
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# If not running, start it
docker compose up -d postgres

# Wait 10 seconds for startup, then retry
```

---

### Migrations already applied

**Error**: `relation "user_session_states" already exists`

**Fix**: This is normal! The migration was already applied. Skip this step.

---

### Can't see draft recovery prompt

**Reason**: Draft hasn't been saved yet or retention expired (24 hours)

**Fix**:
1. Type in form
2. Wait at least 10 seconds to see "Saved"
3. Then close and reopen tab

---

## 📚 Next Steps

- **Full Testing**: See `IMPLEMENTATION_SUMMARY.md` for comprehensive test scenarios
- **Development**: See `specs/001-smooth-workflow/` for technical details
- **Configuration**: See `.env` files for environment variables
- **Tasks**: See `specs/001-smooth-workflow/tasks.md` for implementation status

---

## 🎉 Success!

If all tests pass, you have a **fully functional workflow optimization system**!

### Key Capabilities

✅ Context-preserving navigation (<500ms)  
✅ Automatic draft saving (10s intervals)  
✅ Draft recovery after interruption  
✅ Conflict detection and resolution  
✅ Performance monitoring  
✅ Actionable error messages  
✅ Undo functionality (5-second window)  
✅ Background task management  

**Ready to build more features or test in production!** 🚀
