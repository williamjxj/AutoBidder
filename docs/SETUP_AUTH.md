# 🚀 Quick Start Guide - Updated Authentication System

## Prerequisites
- Docker & Docker Compose installed
- Python 3.11+ installed
- Node.js 20+ installed

## Step 1: Start Docker Services (PostgreSQL + ChromaDB)

```bash
cd /Users/william.jiang/my-apps/auto-bidder
docker-compose up -d
```

**Verify services are running:**
```bash
docker-compose ps
```

You should see:
- `auto-bidder-postgres` on port 5432
- `auto-bidder-chromadb` on port 8001

## Step 2: Database is Ready! ✅

The custom users table has been created and migration applied successfully.

**Verify the schema:**
```bash
docker exec -it auto-bidder-postgres psql -U postgres -d auto_bidder_dev -c "\dt"
```

You should see:
- `users` table
- `user_profiles` table
- `projects` table

## Step 3: Install Backend Dependencies

```bash
cd backend

# If using virtualenv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (includes new JWT packages)
pip install -r requirements.txt
```

**New packages added:**
- `python-jose[cryptography]` - JWT token handling
- `passlib[bcrypt]` - Password hashing
- `asyncpg` - PostgreSQL async driver
- `sqlalchemy[asyncio]` - SQLAlchemy with async support

## Step 4: Start Backend Server

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

**You should see:**
```
🚀 Auto-Bidder AI Service starting...
✅ Database connection pool initialized
```

**Test the API:**
```bash
# Health check
curl http://localhost:8000/health

# API docs
open http://localhost:8000/docs
```

## Step 5: Start Frontend

```bash
cd frontend
npm install  # First time only
npm run dev
```

**Frontend runs on:** `http://localhost:3000`

## Step 6: Test Authentication

### Option A: Use the UI

1. Go to `http://localhost:3000`
2. Click "Get Started" or "Sign Up"
3. Create an account with:
   - Email: `test@example.com`
   - Password: `password123` (min 8 chars)
4. You'll be logged in and redirected to `/dashboard`

### Option B: Use curl (Backend API)

**Signup:**
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "full_name": "Test User"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

**Response includes:**
- `access_token` - JWT token (expires in 7 days)
- `user` - User object with id, email, etc.

**Get current user:**
```bash
# Use the token from login response
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## ✅ Verification Checklist

- [ ] PostgreSQL running on `localhost:5432`
- [ ] ChromaDB running on `localhost:8001`
- [ ] Backend running on `http://localhost:8000`
- [ ] Frontend running on `http://localhost:3000`
- [ ] Can signup new user
- [ ] Can login with email/password
- [ ] JWT token received
- [ ] Can access protected routes after login

## 🔧 Environment Variables

### Backend (.env) - Already Configured ✅

```bash
DATABASE_URL=postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/auto_bidder_dev
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production-please
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=10080
# ... other settings
```

### Frontend (.env.local) - Already Configured ✅

```bash
NEXT_PUBLIC_BACKEND_API_URL=http://localhost:8000
PYTHON_AI_SERVICE_URL=http://localhost:8000
# ... other settings
```

## 🎯 What's Different Now?

### Before (Supabase)
- Required Supabase CLI and local Supabase instance
- Auth handled by Supabase Auth server on port 54321
- Used `auth.users` table from Supabase

### After (Custom JWT)
- Uses docker-compose PostgreSQL directly (port 5432)
- Auth handled by FastAPI backend on port 8000
- Custom `users` table with JWT tokens
- No Supabase dependencies

## 🐛 Common Issues

### Backend: "Failed to create database pool"
**Solution:**
```bash
# Ensure PostgreSQL is running
docker-compose ps

# Check connection
docker exec -it auto-bidder-postgres psql -U postgres -d auto_bidder_dev -c "SELECT 1;"
```

### Backend: "JWT_SECRET not found"
**Solution:**
- Check that `JWT_SECRET` exists in `backend/.env`
- The current value is already set (but change in production!)

### Frontend: "Network Error" or "Failed to fetch"
**Solution:**
- Ensure backend is running: `curl http://localhost:8000/health`
- Check `.env.local` has `NEXT_PUBLIC_BACKEND_API_URL=http://localhost:8000`

### Frontend: "Unauthorized" after login
**Solution:**
- Check browser DevTools → Application → Local Storage
- Should see `auth_token` stored
- Try clearing localStorage and login again

## 🎉 Success!

If you can signup/login through the UI and see your dashboard, **everything is working!**

Authentication flow:
1. User signs up → Backend creates user in `users` table
2. Backend generates JWT token with user info
3. Frontend stores token in localStorage + cookie
4. Frontend includes token in API requests: `Authorization: Bearer TOKEN`
5. Backend validates token and returns user data

---

**Next Steps:**
- See [AUTH_MIGRATION.md](AUTH_MIGRATION.md) for detailed technical changes
- Update JWT_SECRET in production (use `openssl rand -hex 32`)
- Test all protected routes (dashboard, projects, etc.)
