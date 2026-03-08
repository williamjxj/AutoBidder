# Implementation Plan: Refactor PostgreSQL Database for UI Alignment

**Branch**: `005-refactor-pg-database` | **Date**: 2026-03-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-refactor-pg-database/spec.md`

## Summary

Refactor the PostgreSQL schema so table names align with UI navigation. Primary changes: (1) Rename `jobs` → `projects` to match Projects nav, (2) Remove legacy `projects` and `bids` tables, (3) Update all FKs and code, (4) Update docs/database-schema-reference.md with nav-to-table mapping.

## Technical Context

**Language/Version**: Python 3.12+ (backend), TypeScript/Next.js (frontend)
**Primary Dependencies**: FastAPI, SQLAlchemy/asyncpg, Next.js 16, TanStack Query
**Storage**: PostgreSQL with pgvector
**Testing**: pytest (backend), Vitest/Playwright (frontend)
**Target Platform**: Web (Vercel-compatible frontend, Docker backend)
**Project Type**: Web application (backend/ + frontend/)
**Performance Goals**: No regression; migrations run in <30s
**Constraints**: Zero downtime migration; preserve existing ETL flows
**Scale/Scope**: ~20 tables; 8 nav items; 2 logical groups (Resources, Bidders)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The project constitution (`.specify/memory/constitution.md`) is a template and not yet ratified. No project-specific gates apply. Proceeding with standard best practices: migrations must be reversible, tests must pass, documentation must be updated.

## Project Structure

### Documentation (this feature)

```text
specs/005-refactor-pg-database/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (migration contract)
└── tasks.md             # Phase 2 output (/speckit.tasks - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── models/          # job.py → project.py (or rename)
│   ├── services/        # job_service.py → project_service.py
│   ├── routers/          # projects.py (no route change)
│   └── etl/             # hf_loader, freelancer - update table refs
└── tests/

frontend/
├── src/
│   ├── app/(dashboard)/  # projects, proposals pages
│   ├── hooks/            # useProjects
│   └── lib/api/          # client.ts
└── tests/

database/
├── migrations/          # 011_* migration for refactor
└── seed/                # dev_data.sql - remove projects/bids, use new schema

docs/
└── database-schema-reference.md  # Full rewrite with nav mapping
```

**Structure Decision**: Web app with backend (FastAPI) and frontend (Next.js). Database migrations in `database/migrations/`. Refactor touches backend services, frontend API types, seed data, and docs.

## Complexity Tracking

> No constitution violations. Table rename is a standard refactor with clear scope.
