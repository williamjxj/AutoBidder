# Makefile Command Reference

> Full command inventory for the Auto-Bidder project.  
> Only the most common commands are in the `Makefile` itself — everything below documents both the core and the full set.

---

## Quick Start

```bash
make infra-up          # Start PostgreSQL + ChromaDB
make install           # Install all dependencies
make dev               # Run both servers (backend :5555 + frontend :5556)
make help              # Show available commands
```

---

## Infrastructure (Docker)

| Command | Description | Notes |
|---------|-------------|-------|
| `make infra-up` | Start PostgreSQL + ChromaDB containers | Detached mode (`-d`) |
| `make infra-down` | Stop all Docker containers | |
| `make infra-logs` | Tail logs from all containers | Press `Ctrl+C` to exit |
| `make infra-ps` | Show running container status | |

---

## Backend

### Development Server

| Command | Description | Notes |
|---------|-------------|-------|
| `make backend-dev` | Start backend with hot-reload (port **5555**) | Uses `$(VENV)/bin/uvicorn` |
| `make backend-dev-venvless` | Start backend assuming venv is already activated | Skips venv path prefix |

### Testing

| Command | Description | Notes |
|---------|-------------|-------|
| `make backend-test` | Run **all** backend tests | Equivalent to `pytest` |
| `make backend-test-unit` | Run only unit tests | Marker: `-m unit` |
| `make backend-test-integration` | Run only integration tests | Marker: `-m integration` |
| `make backend-test-cov` | Run tests with coverage report | Outputs term-missing + HTML |

### Code Quality

| Command | Description | Notes |
|---------|-------------|-------|
| `make backend-lint` | Lint with ruff | Checks all `.py` files |
| `make backend-format` | Format with black | Modifies files in-place |
| `make backend-format-check` | Check formatting (no changes) | CI-friendly |
| `make backend-typecheck` | Type-check with mypy | Scans `app/` |

### Database Migrations

| Command | Description | Notes |
|---------|-------------|-------|
| `make backend-migrate` | Apply pending DB migrations | Runs `scripts/run_migrations.py` |

### Utilities

| Command | Description | Notes |
|---------|-------------|-------|
| `make backend-venv` | Create Python virtual environment | At `backend/venv/` |
| `make backend-install` | Install Python dependencies | Uses `uv` if available, else `pip` |
| `make backend-shell` | Quick config sanity check | Loads settings from `.env` |
| `make backend-clean` | Remove `__pycache__`, `.pytest_cache`, builds | |

---

## Frontend

| Command | Description | Notes |
|---------|-------------|-------|
| `make frontend-install` | Install npm dependencies | Runs `npm install` |
| `make frontend-dev` | Start dev server (port **5556**) | |
| `make frontend-build` | Production build | |
| `make frontend-start` | Serve production build | |
| `make frontend-lint` | ESLint check | |
| `make frontend-typecheck` | TypeScript type checking | |
| `make frontend-clean` | Remove `.next` and `node_modules` | |

---

## Combined (All-at-once)

| Command | Description | Notes |
|---------|-------------|-------|
| `make install` | Install **all** dependencies (backend + frontend) | |
| `make dev` | Start **both** dev servers concurrently | Backend :5555 + Frontend :5556 |
| `make lint` | Lint both projects | |
| `make format` | Format backend code | |
| `make typecheck` | Type-check both projects | |
| `make test` | Run backend tests | |
| `make clean` | Clean artifacts from both projects | |

---

## Database

| Command | Description | Notes |
|---------|-------------|-------|
| `make db-migrate` | Apply migrations | Alias for `backend-migrate` |
| `make db-reset` | **Destroy + recreate** DB volumes | ⚠️ Wipes all data |
| `make db-psql` | Open `psql` shell in running container | Connects to `auto_bidder_dev` |
| `make db-migration-create name=xxx` | Create a new timestamped SQL migration file | Creates `database/migrations/<ts>_xxx.sql` |

---

## Utility Scripts

| Command | Description | Notes |
|---------|-------------|-------|
| `make scripts-backend-start` | Start backend via `scripts/backend-start.sh` | Convenience wrapper |
| `make scripts-railway-setup` | Run Railway deployment setup script | |
| `make etl-hf` | Run HuggingFace dataset ETL | |
| `make etl-freelancer` | Run Freelancer scraper ETL | |
| `make email-test` | Test Resend email configuration | |

---

## Health / API

| Command | Description | Notes |
|---------|-------------|-------|
| `make health` | Check backend health endpoint | `GET /health` |
| `make health-swagger` | Open Swagger UI in browser | `http://localhost:5555/docs` |

---

## Help

| Command | Description | Notes |
|---------|-------------|-------|
| `make help` | List all available commands | Parses `##` comments in Makefile |

---

## Quick Reference (most-used)

```bash
# First time
make infra-up && make install

# Daily development
make dev                 # Both servers
make backend-test        # Run tests
make lint                # Quick lint

# Database
make db-psql             # Inspect data
make db-migrate          # Apply migrations

# Health
make health              # Is the backend up?
```

---

## Tips

- **Port conflicts?** Backend = `5555`, Frontend = `5556`. Both are uncommon ports to avoid collisions.
- **`make help`** greps the Makefile for `##` comments. If you add a new target, add a `## Description` to get auto-documented.
- **Combined commands** (`make dev`, `make lint`, etc.) run sub-targets — check they're available before running the combined version.
