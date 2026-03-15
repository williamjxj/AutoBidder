# Documentation Index

Agentic Proposal Engine documentation. Brief, key-point focused.

**Last Updated**: March 2026

---

## Structure

### Architecture & Setup
- [diagrams/architecture-diagram.md](diagrams/architecture-diagram.md) — System overview
- [diagrams/workflow-diagram.md](diagrams/workflow-diagram.md) — Projects + proposal workflow
- [diagrams/auth-flow-diagram.md](diagrams/auth-flow-diagram.md) — Authentication sequence
- [database-schema-reference.md](database-schema-reference.md) — PostgreSQL schema
- [chromadb.md](chromadb.md) — Vector DB (modes, setup, upgrade, troubleshooting)
- [setup-and-run.md](setup-and-run.md) — Quick start
- [setup-auth.md](setup-auth.md) — Auth
- [railway-deployment-guide.md](railway-deployment-guide.md) — **Deployment (recommended)**

### AI & Features
- [knowledge-base.md](knowledge-base.md) — Knowledge base management
- [proposals.md](proposals.md) — Proposal workflow & generation
- [projects.md](projects.md) — Projects loading/discovery behavior and ETL sources
- [autonomous-automation-strategy.md](autonomous-automation-strategy.md) — Autonomous bidding
- [huggingface-job-discovery.md](huggingface-job-discovery.md) — Job discovery
- [etl-scheduler-guide.md](etl-scheduler-guide.md) — ETL pipelines

### UI & Operations
- [dashboard.md](dashboard.md) — Dashboard features
- [analytics.md](analytics.md) — Analytics
- [keywords.md](keywords.md) — Keyword management
- [strategies.md](strategies.md) — Proposal strategy management
- [settings.md](settings.md) — Preferences and credentials
- [email-system.md](email-system.md) — Email config

### Dashboard Page Coverage

| UI Page | Primary Doc |
|---|---|
| `/dashboard` | [dashboard.md](dashboard.md) |
| `/projects` | [projects.md](projects.md) |
| `/proposals` and `/proposals/new` | [proposals.md](proposals.md) |
| `/knowledge-base` | [knowledge-base.md](knowledge-base.md) |
| `/analytics` | [analytics.md](analytics.md) |
| `/keywords` | [keywords.md](keywords.md) |
| `/strategies` | [strategies.md](strategies.md) |
| `/settings` | [settings.md](settings.md) |

### Guides & Planning
- [user-guides.md](user-guides.md) — End-user guide
- [diagrams/](diagrams/) — Workflows, auth flows, quickstart
- [todos/](todos/) — Task lists, specs

---

## Quick Navigation

**New developers:** [setup-and-run.md](setup-and-run.md) → [architecture-diagram.md](diagrams/architecture-diagram.md) → [database-schema-reference.md](database-schema-reference.md)

**Deployment:** [railway-deployment-guide.md](railway-deployment-guide.md) | [setup-auth.md](setup-auth.md) | [chromadb.md](chromadb.md)

**Business:** [business-plan/README.md](business-plan/README.md)
