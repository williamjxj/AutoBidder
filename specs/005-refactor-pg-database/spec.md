# Feature Specification: Refactor PostgreSQL Database for UI Alignment

**Feature Branch**: `005-refactor-pg-database`  
**Created**: 2026-03-07  
**Status**: Draft  
**Input**: User description: "adjust, refactor pg database based on Browser UI, postgresql tables, docs/database-schema-reference.md and 2 groups: resources, bidders. analyse all the pg tables, and do reactor/adjust the tables"

## Summary

Refactor the PostgreSQL schema so table names and structure align with the UI navigation. Remove unused tables, consolidate confusing dual workflows (jobs vs projects, proposals vs bids), and ensure a clear mapping between sidebar nav items and database tables.

## Current State Analysis

### UI Navigation (from app-sidebar)

| Nav Item       | Route           | Current Backend Table(s)        | Mismatch? |
|----------------|-----------------|----------------------------------|-----------|
| Dashboard      | /dashboard      | Aggregates from multiple        | No        |
| Projects       | /projects       | `jobs` (API returns `jobs`)     | **Yes** — UI says "Projects" but table is `jobs` |
| Proposals       | /proposals      | `proposals`                      | No        |
| Knowledge Base | /knowledge-base | `knowledge_base_documents`       | No        |
| Strategies     | /strategies     | `bidding_strategies`             | No        |
| Keywords       | /keywords       | `keywords`                      | No        |
| Analytics      | /analytics      | `workflow_analytics`, `analytics_events` | No |
| Settings       | /settings       | `user_profiles`, `platform_credentials` | No |

### Confusion: jobs, projects, etl_runs

- **jobs**: ETL-fed job listings (HuggingFace, Freelancer). Source of truth for Projects UI. Backend `job_service` reads from `jobs`.
- **projects**: Legacy table for user-saved/curated job postings. **Not used by Projects page** — only in seed data. Different schema (user_id, manual entry).
- **etl_runs**: ETL audit trail (backend only). Not a UI concept — keep for ops.
- **bids**: Linked to `projects`. Proposals UI uses `proposals` (linked to `jobs`). Dual workflow: `bids` + `projects` vs `proposals` + `jobs`.

### Two Groups (Resources vs Bidders)

- **Resources**: Dashboard, Projects, Knowledge Base, Keywords, Analytics, Settings — discovery, context, configuration.
- **Bidders**: Proposals, Strategies — bidding and proposal creation.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Clear Table-to-Nav Mapping (Priority: P1)

As a developer or stakeholder, I want each sidebar nav item to map to a single, clearly named table (or small set) so that I can understand the data model without confusion.

**Why this priority**: Eliminates the jobs/projects/etl_runs confusion and reduces onboarding time.

**Independent Test**: Can be verified by inspecting docs/database-schema-reference.md and confirming each nav item has a documented table mapping with no ambiguity.

**Acceptance Scenarios**:

1. **Given** the Projects nav, **When** I read the schema docs, **Then** I see exactly which table(s) back it and the naming is consistent.
2. **Given** the Proposals nav, **When** I read the schema docs, **Then** I see one primary table (proposals) with no duplicate concept (bids).

---

### User Story 2 - Remove Unused Tables (Priority: P1)

As a maintainer, I want unused tables removed so the schema stays lean and I don't accidentally reference legacy structures.

**Why this priority**: Reduces cognitive load and prevents future bugs from using wrong tables.

**Independent Test**: Run application and verify all features work; confirm no code references dropped tables.

**Acceptance Scenarios**:

1. **Given** the `projects` table (legacy, unused by Projects UI), **When** refactor is complete, **Then** it is removed and all code updated.
2. **Given** the `bids` table (linked to projects), **When** refactor is complete, **Then** it is removed or consolidated into proposals, and code updated.

---

### User Story 3 - Documentation Accuracy (Priority: P2)

As a developer, I want docs/database-schema-reference.md to accurately reflect the final schema, including table purposes, relationships, and nav mappings.

**Why this priority**: Ensures the refactor is discoverable and maintainable.

**Independent Test**: Compare schema doc against actual migrations; all tables documented, no stale references.

**Acceptance Scenarios**:

1. **Given** the refactored schema, **When** I read the schema doc, **Then** every table is listed with correct purpose and nav mapping.
2. **Given** removed tables, **When** I search the doc, **Then** they are not mentioned (or marked deprecated with migration path).

---

### Edge Cases

- What happens when ETL runs and writes to the projects/jobs table during migration? Migration must be sequenced to avoid data loss.
- How does the system handle existing seed data that references `projects` and `bids`? Seed script must be updated to use new schema.
- What if `scraping_jobs` or `platform_credentials` are used by future features? Audit usage before removal; only remove if confirmed unused.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The table backing the Projects nav MUST have a name that matches or clearly corresponds to "Projects" (e.g., `projects` for job listings).
- **FR-002**: There MUST be exactly one primary table for user-created proposals/bids — no dual `proposals` + `bids` with overlapping purpose.
- **FR-003**: Unused tables (`projects` as currently defined, `bids` if redundant with proposals) MUST be removed after migration.
- **FR-004**: The `etl_runs` table MUST be retained for ETL audit; it is not required to map to a nav item.
- **FR-005**: All code (backend, frontend, seeds) MUST be updated to reference the new schema.
- **FR-006**: docs/database-schema-reference.md MUST be updated to reflect the final schema and nav-to-table mapping.
- **FR-007**: Tables MUST be logically grouped as Resources (projects, keywords, knowledge_base_documents, analytics, etc.) and Bidders (proposals, bidding_strategies) in documentation.

### Key Entities

- **Project (job listing)**: A freelance job opportunity from ETL or discovery. Attributes: platform, external_id, title, description, budget, skills, status. Backs Projects nav.
- **Proposal**: A user's bid/proposal for a project. Attributes: content, strategy, status, link to project. Backs Proposals nav.
- **ETL Run**: Audit record for an ETL execution. Attributes: source, started_at, completed_at, counts. Backend-only.
- **Keyword**: User-defined search term. Backs Keywords nav.
- **Bidding Strategy**: AI prompt config for proposals. Backs Strategies nav.
- **Knowledge Base Document**: Uploaded file for RAG. Backs Knowledge Base nav.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer can identify which table backs each nav item in under 30 seconds using the schema doc.
- **SC-002**: Zero references to removed tables (`projects`, `bids`) in application code after refactor.
- **SC-003**: All existing user flows (discover projects, create proposal, view strategies, etc.) work identically after migration.
- **SC-004**: docs/database-schema-reference.md has a nav-to-table mapping section that is complete and accurate.

## Assumptions

- The Projects UI will continue to display job listings from ETL (HuggingFace, Freelancer). The refactor aligns naming, not behavior.
- `proposals` is the canonical table for the Proposals nav; `bids` can be deprecated if its data is migrated or redundant.
- `scraping_jobs` is not actively used by the current Projects/Proposals flow; it can be retained for future use or removed if confirmed unused.
- Migration will be done via new migration files; no in-place renames without data migration steps.
