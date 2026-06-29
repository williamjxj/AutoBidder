# =============================================================================
# Auto-Bidder Makefile
# =============================================================================
# Core daily commands only. For the full command reference see:
#   docs/makefile-commands.md
# =============================================================================

.DEFAULT_GOAL := help

# ─── Paths ──────────────────────────────────────────────────────────────────
BACKEND     := backend
FRONTEND    := frontend
VENV        := $(BACKEND)/venv

# ─── Colors for help output ─────────────────────────────────────────────────
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RESET := \033[0m

# =============================================================================
# Infrastructure (Docker)
# =============================================================================

infra-up: ## Start Docker services (PostgreSQL + ChromaDB)
	docker-compose up -d

infra-down: ## Stop Docker services
	docker-compose down

# =============================================================================
# Backend
# =============================================================================

backend-dev: ## Start backend dev server (uvicorn with hot-reload, port 5555)
	$(VENV)/bin/uvicorn app.main:app --reload --port 5555 --app-dir $(BACKEND)

backend-test: ## Run all backend tests
	cd $(BACKEND) && $(VENV)/bin/pytest

backend-lint: ## Lint backend with ruff
	cd $(BACKEND) && $(VENV)/bin/ruff check .

backend-format: ## Format backend with black
	cd $(BACKEND) && $(VENV)/bin/black .

backend-typecheck: ## Run mypy type checking
	cd $(BACKEND) && $(VENV)/bin/mypy app

backend-migrate: ## Apply database migrations
	$(VENV)/bin/python $(BACKEND)/scripts/run_migrations.py

# =============================================================================
# Frontend
# =============================================================================

frontend-dev: ## Start frontend dev server (port 5556)
	cd $(FRONTEND) && npm run dev -- --port 5556

frontend-lint: ## Lint frontend with ESLint
	cd $(FRONTEND) && npm run lint

frontend-typecheck: ## TypeScript type checking
	cd $(FRONTEND) && npm run type-check

# =============================================================================
# Combined / All-at-once
# =============================================================================

install: ## Install all dependencies (backend + frontend)
	@if command -v uv &> /dev/null; then \
		uv pip install -r $(BACKEND)/requirements.txt; \
	else \
		$(VENV)/bin/pip install -r $(BACKEND)/requirements.txt; \
	fi
	cd $(FRONTEND) && npm install

dev: ## Start all dev servers (backend + frontend concurrently)
	@echo "$(YELLOW)Starting backend (port 5555) and frontend (port 5556)...$(RESET)"
	@echo "$(YELLOW)Open http://localhost:5556 in your browser.$(RESET)"
	@trap 'kill 0' EXIT; \
		$(MAKE) backend-dev & \
		$(MAKE) frontend-dev & \
		wait

lint: backend-lint frontend-lint ## Lint both backend and frontend

format: backend-format ## Format backend code

typecheck: backend-typecheck frontend-typecheck ## Type check both projects

test: backend-test ## Run backend tests

clean: ## Clean build artifacts from both projects
	find $(BACKEND) -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find $(BACKEND) -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf $(BACKEND)/*.egg-info $(BACKEND)/.coverage $(BACKEND)/htmlcov
	rm -rf $(FRONTEND)/.next

# =============================================================================
# Database
# =============================================================================

db-migrate: backend-migrate ## Apply database migrations (alias for backend-migrate)

db-psql: ## Open psql shell in the running postgres container
	docker exec -it auto-bidder-postgres psql -U postgres -d auto_bidder_dev

# =============================================================================
# Health Check
# =============================================================================

health: ## Check backend health
	curl -s http://localhost:5555/health | python3 -m json.tool || echo "$(YELLOW)Backend not running at :5555$(RESET)"

# =============================================================================
# Help
# =============================================================================

help: ## Show this help message
	@printf "\n$(BLUE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)\n"
	@printf "$(BLUE)  Auto-Bidder — Available Commands$(RESET)\n"
	@printf "$(BLUE)  Full reference: docs/makefile-commands.md$(RESET)\n"
	@printf "$(BLUE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)\n\n"
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		sort | \
		awk 'BEGIN {FS = ":.*?## "}; \
			{printf "  $(GREEN)%-28s$(RESET) %s\n", $$1, $$2}'
	@printf "\n$(BLUE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)\n"
	@printf "  Quick start:  $(YELLOW)make infra-up && make install && make dev$(RESET)\n"
	@printf "$(BLUE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)\n\n"
