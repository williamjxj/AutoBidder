# Auto-Bidder Development Guide

## Project Structure

```
backend/              # FastAPI Python service (app/main.py entrypoint)
frontend/             # Next.js 15 / React 19 app
database/migrations/  # PostgreSQL schema migrations
backend/scripts/      # ETL and utility scripts
backend/tests/        # unit/, integration/
docs/                # Architecture, guides, and diagrams
```

## Commands

All commands available via `make`:
```bash
make help         # List everything
make dev          # Start both servers
make test         # Run backend tests
make lint         # Lint both projects
```

### Raw commands (backends)

```bash
# Backend
make backend-dev       # uvicorn app.main:app --reload --port 5555
make backend-test      # pytest
make backend-lint      # ruff check .
make backend-format    # black .
make backend-typecheck # mypy app
make backend-migrate   # Apply DB migrations

# Frontend
make frontend-dev       # npm run dev (localhost:5556)
make frontend-lint      # npm run lint
make frontend-typecheck # tsc --noEmit

# Infrastructure
make infra-up           # docker-compose up -d
make infra-down         # docker-compose down
```

> 💡 Full reference: [docs/makefile-commands.md](docs/makefile-commands.md)

## Required Environment Variables

### Backend (`backend/.env`)
- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET` - Authentication secret
- `LLM_PROVIDER` - `deepseek` or `openai`
- `DEEPSEEK_API_KEY` or `OPENAI_API_KEY` - LLM API key
- `CHROMA_PERSIST_DIR` - Vector DB storage path
- `RESEND_API_KEY` - Email delivery
- `FROM_EMAIL` - Must be `service@bestitconsulting.ca` (verified Resend domain)

### Frontend (`frontend/.env.local`)
- `NEXT_PUBLIC_BACKEND_API_URL=http://localhost:5555`

## Tech Stack

| Layer | Technologies |
|-------|--------------|
| Frontend | Next.js 15, React 19, TypeScript, TailwindCSS 4, TanStack Query |
| Backend | FastAPI, SQLAlchemy (async), asyncpg, Pydantic v2 |
| Vector DB | ChromaDB 0.4+ |
| RAG | LangChain, SentenceTransformer embeddings |
| LLM | DeepSeek / OpenAI GPT-4 |
| Auth | JWT with bcrypt |

## Code Style

| Tool | Config |
|------|--------|
| Python lint | ruff (`pyproject.toml` - line-length 100) |
| Python format | black (line-length 100) |
| Python types | mypy with pydantic plugin |
| JS/TS lint | ESLint (`next/core-web-vitals`) |
| JS/TS format | Prettier (`semi: false`, `singleQuote: true`, `printWidth: 100`) |

## Testing

- `pytest` with markers: `unit`, `integration`, `slow`
- Test files: `backend/tests/unit/` and `backend/tests/integration/`
- Run single test: `pytest backend/tests/unit/test_file.py`

## Database

- Migrations live in `database/migrations/`
- Apply manually via `psql` or `python backend/scripts/run_migrations.py`
- Docker: `docker exec -i auto-bidder-postgres psql -U postgres -d auto_bidder_dev < path/to/migration.sql`

## API Documentation

- Swagger UI: http://localhost:5555/docs
- ReDoc: http://localhost:5555/redoc
- Health check: http://localhost:5555/health

## Key Conventions

1. **LLM Provider**: Default is DeepSeek; OpenAI is alternative. Set via `LLM_PROVIDER` env var.
2. **Email**: Always use `service@bestitconsulting.ca` as FROM address (verified domain).
3. **ChromaDB**: Per-user collections; `EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2`
4. **Job Discovery**: HuggingFace datasets by default (`USE_HF_DATASET=true`)
