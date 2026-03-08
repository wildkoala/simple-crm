# Security

## Authentication

### JWT Tokens

- Tokens are signed with HMAC-SHA256 using the `SECRET_KEY`.
- Default expiration is 60 minutes (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`).
- Tokens are stored in the browser's `localStorage`.

### API Keys

- API keys are prefixed with `crm_` for easy identification.
- Keys are hashed with HMAC-SHA256 before storage -- the raw key is never stored.
- One API key per user.

### Password Security

- Passwords are hashed with bcrypt (via passlib).
- Minimum length: 8 characters (enforced by Pydantic schema validation).
- Password reset tokens are hashed before storage and expire after 24 hours.

### Google Sign-In

- Google ID tokens are verified against Google's public keys.
- Only tokens with verified email addresses are accepted.
- The `GOOGLE_CLIENT_ID` audience is validated to prevent token reuse from other applications.

## Rate Limiting

Sensitive endpoints are rate-limited:

| Endpoint | Limit |
|----------|-------|
| `POST /auth/login` | 5 requests/minute |
| `POST /auth/google` | 10 requests/minute |
| `POST /auth/password-reset-request` | 3 requests/minute |
| `POST /auth/password-reset` | 5 requests/minute |

## Authorization

- All API endpoints require authentication.
- Users can only modify resources they created (accounts, vehicles, compliance records, teaming, proposals).
- Admin users can modify any resource.
- Admin-only operations: user management, opportunity restore, audit log access.

## File Upload Security

- Uploaded files are stored with randomized filenames to prevent enumeration.
- Path traversal attacks are mitigated with `os.path.realpath()` validation.
- File downloads require authentication.

## CORS

- CORS is restricted to the configured `FRONTEND_URL` and any `EXTRA_CORS_ORIGINS`.
- Only specific HTTP methods and headers are allowed.

## Audit Logging

Sensitive operations are recorded in the audit log:

- Deleting accounts, contacts, opportunities, and contracts.
- Restoring soft-deleted opportunities.

Each audit entry includes the user ID, action, entity type/ID, and timestamp.

## Recommendations

1. **Use HTTPS** in production. Configure TLS termination at your load balancer or reverse proxy.
2. **Rotate `SECRET_KEY`** periodically. Note that rotating invalidates all existing JWT tokens and API keys.
3. **Use PostgreSQL** in production. SQLite is not suitable for concurrent access.
4. **Restrict database access** to only the backend service.
5. **Monitor audit logs** for suspicious delete activity.
6. **Set `ENV=production`** to prevent seed data from being loaded.
7. **Configure SMTP** for password reset functionality -- without it, users cannot reset forgotten passwords.
