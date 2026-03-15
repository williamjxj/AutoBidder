# Keywords - User Guide

Last Updated: March 2026

Keywords help personalize project discovery and AI proposal generation.

## What Keywords Do

1. Projects filtering fallback
- When you do not enter a search term on Projects, the backend can use your active keywords.
- This improves relevance without manual typing each time.

2. Proposal generation context
- Active keywords are included as signal for skill emphasis in AI-generated proposals.

3. Dashboard setup progress
- Keywords are part of setup completeness checks and dashboard onboarding flow.

## Core Features

- Create keyword (`POST /api/keywords`)
- List keywords (`GET /api/keywords`)
- Update keyword (`PATCH /api/keywords/{id}`)
- Delete keyword (`DELETE /api/keywords/{id}`)
- Toggle active/inactive state
- Optional match type/description metadata

## Best Practices

- Keep 5-15 high-signal keywords aligned to your actual services.
- Prefer specific terms (`fastapi`, `nextjs`, `rag`, `aws`) over broad terms (`software`).
- Deactivate outdated terms instead of deleting immediately.
- Review monthly to keep suggestions relevant.

## Troubleshooting

- No change in Projects results:
  - Ensure keywords are active.
  - Confirm search box is empty if you want keyword fallback behavior.
- Too many irrelevant matches:
  - Remove generic terms.
  - Use more specific stack/domain keywords.

## Related Docs

- [projects.md](./projects.md)
- [proposals.md](./proposals.md)
- [dashboard.md](./dashboard.md)
