# Infra Reference — Docker Compose + Vercel + Railway

## Local Dev with Docker Compose

```
docker-compose.yml services:
  frontend   → Next.js dev server  (port 3000)
  backend    → FastAPI / uvicorn   (port 8000)
  db         → PostgreSQL 15       (port 5432)
  chromadb   → ChromaDB server     (port 8001)
```

### Common commands
```bash
docker compose up --build          # Full rebuild (after dep changes)
docker compose up                  # Normal start (uses cached images)
docker compose down                # Stop all services
docker compose down -v             # Stop + delete volumes (fresh DB)
docker compose logs backend -f     # Tail backend logs
docker compose logs frontend -f    # Tail frontend logs
docker compose exec db psql -U postgres autobidder  # Direct DB access
```

## Environment Variables

### Repo root `.env` (shared by Docker Compose)
```
POSTGRES_DB=autobidder
POSTGRES_USER=postgres
POSTGRES_PASSWORD=secret

SECRET_KEY=<random 32-char hex>
ACCESS_TOKEN_EXPIRE_MINUTES=1440

OPENAI_API_KEY=sk-...
DEEPSEEK_API_KEY=...

RESEND_API_KEY=re_...
RESEND_FROM_EMAIL=you@yourdomain.com
RESEND_BCC_EMAIL=archive@yourdomain.com

CHROMA_HOST=chromadb
CHROMA_PORT=8001
```

### `frontend/.env.local` (Next.js, not in Docker Compose)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Production env vars
- **Vercel (frontend):** Set `NEXT_PUBLIC_API_URL` to your Railway backend URL
- **Railway (backend):** All root `.env` vars, plus `DATABASE_URL` injected by Railway

## Deployment

### Frontend → Vercel
```bash
cd frontend
vercel --prod
# Vercel auto-detects Next.js; set env vars in Vercel dashboard
```

### Backend → Railway
- Connect GitHub repo in Railway dashboard
- Set root directory to `backend/`
- Railway auto-reads `railway.toml` for build/start commands
- Add all env vars from `.env` in Railway dashboard
- DATABASE_URL is injected automatically when you add a Railway PostgreSQL plugin

### Database → Railway PostgreSQL
- Add PostgreSQL plugin in Railway
- Run migrations: `railway run bash scripts/migrate.sh`

## Health Checks

```bash
# Backend alive?
curl http://localhost:8000/health

# ChromaDB alive?
curl http://localhost:8001/api/v1/heartbeat

# Frontend alive?
curl http://localhost:3000

# DB connected?
docker compose exec db pg_isready -U postgres
```
