# API Contracts: Autonomous Bidding Improvements

**Feature**: 004-improve-autonomous  
**Spec**: [../spec.md](../spec.md)

## Contracts

| File | Purpose |
|------|---------|
| `autonomous-api.yaml` | Autonomous pipeline endpoints: start, status, run history |
| `autonomy-settings-api.yaml` | User autonomy settings: discovery, qualification, notifications, auto-generate |

## Integration

- **Settings API** (`/api/settings/autonomy`) extends existing `settings_service` and `user_profiles.preferences` JSONB
- **Autonomous API** (`/api/autonomous/*`) is a new router; backend scheduler invokes the pipeline internally

## Related

- Projects API: [../../003-projects-etl-persistence/contracts/projects-api.yaml](../../003-projects-etl-persistence/contracts/projects-api.yaml)
- Proposals API: existing `/api/proposals` for proposal CRUD
