# Configuration

All configuration is managed through environment variables, typically set in `backend/.env`.

## Required Settings

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | JWT signing key. Must be unique and secret. | `python -c "import secrets; print(secrets.token_hex(32))"` |
| `DATABASE_URL` | Database connection string. | `postgresql://user:pass@localhost/crm` |

## Optional Settings

### Application

| Variable | Default | Description |
|----------|---------|-------------|
| `ALGORITHM` | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | JWT token lifetime in minutes |
| `FRONTEND_URL` | `http://localhost:5173` | Frontend URL for CORS |
| `EXTRA_CORS_ORIGINS` | *(empty)* | Comma-separated additional CORS origins |
| `ENV` | `development` | Set to `production` to disable seed data |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |

### Google Integration

| Variable | Default | Description |
|----------|---------|-------------|
| `GOOGLE_CLIENT_ID` | *(empty)* | Google OAuth2 client ID (for Sign-In and Gmail) |
| `GOOGLE_CLIENT_SECRET` | *(empty)* | Google OAuth2 client secret (for Gmail) |
| `GOOGLE_REDIRECT_URI` | `http://localhost:8000/gmail/callback` | Gmail OAuth callback URL |
| `GOOGLE_PUBSUB_TOPIC` | *(empty)* | Google Pub/Sub topic for Gmail push notifications |

See [Google Authentication Setup](./google-auth-setup.md) and [Gmail Integration Setup](./gmail-setup.md) for details.

### Email (SMTP)

| Variable | Default | Description |
|----------|---------|-------------|
| `SMTP_SERVER` | `smtp.gmail.com` | SMTP server hostname |
| `SMTP_PORT` | `587` | SMTP server port |
| `SMTP_USERNAME` | *(empty)* | SMTP username |
| `SMTP_PASSWORD` | *(empty)* | SMTP password |
| `SMTP_FROM_EMAIL` | `noreply@pretorin.com` | Sender email address |
| `SMTP_FROM_NAME` | `Pretorin CRM` | Sender display name |

When SMTP credentials are not configured, the system runs in development mode and prints password reset emails to the console.

### Frontend

The frontend uses a single environment variable:

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_BASE_URL` | `http://localhost:8000` | Backend API URL |
| `VITE_GOOGLE_CLIENT_ID` | *(empty)* | Google client ID -- shows Google Sign-In button on login page when set |

Set frontend variables in `frontend/.env.local` or as build-time environment variables.

> **Note:** The Google Sign-In button on the login page is only visible when `VITE_GOOGLE_CLIENT_ID` is set. If omitted, users will only see the email/password form.

## Production Checklist

1. Generate a strong `SECRET_KEY` -- never use the default.
2. Set `ENV=production` to disable seed data.
3. Use PostgreSQL, not SQLite.
4. Set `FRONTEND_URL` to your actual frontend domain.
5. Configure SMTP for password reset emails.
6. Use HTTPS in production -- update `GOOGLE_REDIRECT_URI` and `FRONTEND_URL` accordingly.
7. Set appropriate `ACCESS_TOKEN_EXPIRE_MINUTES` for your security requirements.
