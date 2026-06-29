# Configuration Guide — Keywords, Strategies & Settings

User-facing configuration pages that shape project discovery, proposal generation, and platform preferences.

---

## Keywords

Keywords personalize project discovery and AI proposal generation.

### What Keywords Do

1. **Projects filtering fallback** — When you do not enter a search term on Projects, the backend can use your active keywords to improve relevance without manual typing each time.
2. **Proposal generation context** — Active keywords are included as signal for skill emphasis in AI-generated proposals.
3. **Dashboard setup progress** — Keywords are part of setup completeness checks and dashboard onboarding flow.

### Core Features

- Create keyword (`POST /api/keywords`)
- List keywords (`GET /api/keywords`)
- Update keyword (`PATCH /api/keywords/{id}`)
- Delete keyword (`DELETE /api/keywords/{id}`)
- Toggle active/inactive state
- Optional match type/description metadata

### Best Practices

- Keep 5-15 high-signal keywords aligned to your actual services.
- Prefer specific terms (`fastapi`, `nextjs`, `rag`, `aws`) over broad terms (`software`).
- Deactivate outdated terms instead of deleting immediately.
- Review monthly to keep suggestions relevant.

### Troubleshooting

- **No change in Projects results:** Ensure keywords are active. Confirm search box is empty if you want keyword fallback behavior.
- **Too many irrelevant matches:** Remove generic terms. Use more specific stack/domain keywords.

---

## Strategies

Strategies define how AI should shape proposal tone, structure, and persuasion style.

### What Strategies Control

- Writing tone (professional, technical, concise, etc.)
- Prompt instructions and style constraints
- Default strategy selection for generation flows

### Core Features

- List strategies (`GET /api/strategies`)
- Create strategy (`POST /api/strategies`)
- Update strategy (`PATCH /api/strategies/{id}`)
- Delete strategy (`DELETE /api/strategies/{id}`)
- Set default (`POST /api/strategies/{id}/set-default`)

### Recommended Workflow

1. Create 2-3 distinct strategies (for example: Technical Deep-Dive, Fast Close, Executive Summary).
2. Set one as default for daily usage.
3. Compare proposal outcomes and iterate wording.
4. Keep prompts specific and measurable.

### Prompt Writing Tips

- **Do:** include target audience and expected length.
- **Do:** specify must-have sections (opening, solution, timeline, CTA).
- **Do not:** over-constrain with conflicting instructions.
- **Do not:** include vague phrases like "make it better" without criteria.

### Troubleshooting

- **Generated text ignores style:** Verify selected strategy is active/default. Reduce conflicting instructions between strategy and form notes.
- **Results too generic:** Add concrete differentiators and proof points in the strategy prompt.

---

## Settings

Settings manages personal preferences and platform credentials used by the system.

### What You Can Configure

1. **User preferences** — Application behavior and profile-level options.
   - Endpoints: `GET /api/settings`, `PUT /api/settings/preferences`

2. **Platform credentials** — Store/update credentials for external platforms. Verify credential connectivity/status.
   - Endpoints:
     - `GET /api/settings/credentials`
     - `POST /api/settings/credentials`
     - `PUT /api/settings/credentials/{id}`
     - `DELETE /api/settings/credentials/{id}`
     - `POST /api/settings/credentials/{id}/verify`

3. **Subscription info** — Read current subscription state.
   - Endpoint: `GET /api/settings/subscription`

### Security Notes

- Credentials are user-scoped and should never be shared across accounts.
- Use verification after updates to confirm credentials are valid.
- Rotate keys periodically and remove unused credentials.

### Troubleshooting

- **Credential verify fails:** Recheck key/token format and scopes. Confirm remote platform has not revoked the key.
- **Preferences not reflected:** Refresh session and verify update succeeded (200 response).

---

## Related Docs

- [projects.md](./projects.md) — Project discovery and filtering
- [proposals.md](./proposals.md) — Proposal generation workflow
- [dashboard.md](./dashboard.md) — Dashboard overview and setup checks
- [database-schema-reference.md](./database-schema-reference.md) — Database schema reference
