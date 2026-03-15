# Settings - User Guide

Last Updated: March 2026

Settings manages personal preferences and platform credentials used by the system.

## What You Can Configure

1. User preferences
- Application behavior and profile-level options
- Endpoint: `GET /api/settings`, `PUT /api/settings/preferences`

2. Platform credentials
- Store/update credentials for external platforms
- Verify credential connectivity/status
- Endpoints:
  - `GET /api/settings/credentials`
  - `POST /api/settings/credentials`
  - `PUT /api/settings/credentials/{id}`
  - `DELETE /api/settings/credentials/{id}`
  - `POST /api/settings/credentials/{id}/verify`

3. Subscription info
- Read current subscription state
- Endpoint: `GET /api/settings/subscription`

## Security Notes

- Credentials are user-scoped and should never be shared across accounts.
- Use verification after updates to confirm credentials are valid.
- Rotate keys periodically and remove unused credentials.

## Troubleshooting

- Credential verify fails:
  - Recheck key/token format and scopes.
  - Confirm remote platform has not revoked the key.
- Preferences not reflected:
  - Refresh session and verify update succeeded (200 response).

## Related Docs

- [dashboard.md](./dashboard.md)
- [setup-auth.md](./setup-auth.md)
- [database-schema-reference.md](./database-schema-reference.md)
