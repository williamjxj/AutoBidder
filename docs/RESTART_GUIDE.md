# Clean Restart Guide 🔄

This guide will help you cleanly restart all services for the auto-bidder project.

## Step 1: Stop All Running Services

### Stop Next.js Frontend
```bash
# Find and kill Next.js process
lsof -ti:3000 | xargs kill -9 2>/dev/null || echo "No process on port 3000"
```

### Stop Python Backend (if running)
```bash
# Find and kill Python/uvicorn process on port 8000
lsof -ti:8000 | xargs kill -9 2>/dev/null || echo "No process on port 8000"
```

### Stop Docker Services
```bash
cd auto-bidder
docker-compose down
```

## Step 2: Clean Up

### Clear Next.js Cache
```bash
cd frontend
rm -rf .next
rm -rf node_modules/.cache
```

### Clear Python Cache (optional)
```bash
cd backend
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
```

## Step 3: Restart Services (Clean Order)

### 1. Start Docker Services (PostgreSQL & ChromaDB)
```bash
cd auto-bidder
docker-compose up -d

# Wait a few seconds for services to start
sleep 5

# Verify services are running
docker-compose ps
```

Expected output:
```
NAME                   IMAGE                    STATUS
auto-bidder-postgres   postgres:15-alpine       Up
auto-bidder-chromadb   chromadb/chroma:latest   Up
```

### 2. Start Python Backend (Terminal 1)
```bash
cd backend
source venv/bin/activate  # or: . venv/bin/activate
uvicorn app.main:app --reload --port 8000

# You should see:
# 🚀 Auto-Bidder AI Service starting...
# ✅ Database connection pool initialized
```

### 3. Start Next.js Frontend (Terminal 2)
```bash
cd frontend
npm run dev

# Should start on http://localhost:3000
```

## Step 4: Verify Everything is Running

### Check Ports
```bash
# Check all ports are in use
lsof -i :3000  # Next.js
lsof -i :8000  # Python Backend
lsof -i :5432  # PostgreSQL
lsof -i :8001  # ChromaDB
```

### Test Endpoints
```bash
# Test backend health
curl http://localhost:8000/health || echo "Backend not responding"

# Test auth endpoint
curl http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}' \
  | python -m json.tool

# Test frontend
curl http://localhost:3000 | head -20 || echo "Frontend not responding"
```

## Quick Restart Script

Save this as `restart.sh`:

```bash
#!/bin/bash
set -e

echo "🛑 Stopping all services..."

# Kill processes
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Stop Docker
cd "$(dirname "$0")"
docker-compose down

echo "🧹 Cleaning caches..."
cd frontend
rm -rf .next
rm -rf node_modules/.cache

echo "🚀 Starting services..."
cd ..
docker-compose up -d
sleep 5

echo "✅ Services restarted!"
echo "📝 Next steps:"
echo "   1. Start backend: cd backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8000"
echo "   2. Start frontend: cd frontend && npm run dev"
```

Make it executable:
```bash
chmod +x restart.sh
```

## Troubleshooting

### Port Already in Use
```bash
# Find what's using the port
lsof -i :3000
lsof -i :8000

# Kill specific process
kill -9 <PID>
```

### Docker Issues
```bash
# Reset Docker services
docker-compose down -v  # Removes volumes too
docker-compose up -d
```

### Next.js Build Issues
```bash
cd frontend
rm -rf .next
rm -rf node_modules
npm install
npm run dev
```
