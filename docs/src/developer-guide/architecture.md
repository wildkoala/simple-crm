# Architecture Overview

Pretorin CRM follows a standard three-tier architecture with a clear separation between frontend, backend, and database.

## System Diagram

```
┌──────────────────┐     HTTP/JSON     ┌──────────────────┐     SQL      ┌──────────────┐
│                  │ ◄──────────────── │                  │ ◄──────────► │              │
│  React Frontend  │                   │  FastAPI Backend  │              │  PostgreSQL   │
│  (Vite + TS)     │ ──────────────►   │  (Python 3.12)    │              │  (or SQLite)  │
│                  │                   │                  │              │              │
└──────────────────┘                   └──────────────────┘              └──────────────┘
      Port 5173                              Port 8000                       Port 5432
   (dev) / 3000                                                              (internal)
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS, shadcn/ui |
| **Backend** | Python 3.12, FastAPI, SQLAlchemy 2.0, Pydantic v2 |
| **Database** | PostgreSQL 16 (production), SQLite (development) |
| **Auth** | JWT (python-jose), bcrypt, Google OAuth2 ID tokens |
| **Email** | Google Gmail API, SMTP (password resets) |
| **Testing** | pytest (backend), Vitest + React Testing Library (frontend) |
| **CI/CD** | GitHub Actions |
| **Deployment** | Docker Compose |

## Directory Structure

```
simple-crm/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application setup
│   │   ├── auth.py              # Authentication utilities
│   │   ├── database.py          # SQLAlchemy engine & session
│   │   ├── email.py             # SMTP email sending
│   │   ├── utils.py             # UUID generation
│   │   ├── seed_data.py         # Demo data seeder
│   │   ├── models/models.py     # SQLAlchemy models
│   │   ├── schemas/schemas.py   # Pydantic request/response schemas
│   │   ├── routers/             # API endpoint handlers
│   │   └── services/            # Business logic (Gmail, SAM.gov, imports)
│   ├── tests/                   # pytest test suite
│   ├── pyproject.toml           # Python project config
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.tsx              # Routes & lazy loading
│   │   ├── main.tsx             # Entry point
│   │   ├── pages/               # Page components
│   │   ├── components/          # Shared components & shadcn/ui
│   │   ├── contexts/            # React contexts (auth)
│   │   └── lib/                 # API client, utilities, badge helpers
│   ├── package.json
│   └── Dockerfile
├── docs/                        # This documentation (mdbook)
├── scripts/                     # Development scripts
├── docker-compose.yml
└── .github/workflows/ci.yml     # CI pipeline
```

## Request Flow

1. User interacts with the React frontend.
2. Frontend calls the backend REST API via `lib/api.ts` (fetch with JWT bearer token).
3. FastAPI routes the request to the appropriate router.
4. Router validates input with Pydantic schemas, checks auth, and calls SQLAlchemy.
5. SQLAlchemy executes queries against PostgreSQL/SQLite.
6. Response is serialized via Pydantic and returned as JSON.

## Key Design Decisions

- **UUIDs for all IDs** -- String(36) UUIDs generated via `utils.generate_id()`. Avoids sequential ID enumeration.
- **Soft deletes on Opportunities** -- Uses `deleted_at` timestamp instead of hard delete. Admins can restore.
- **SQL aggregation for metrics** -- Pipeline metrics are computed in the database, not in-memory.
- **Lazy loading** -- All frontend pages use `React.lazy()` for code splitting.
- **Per-user Gmail** -- Each user connects their own Gmail account independently.
- **Creator-based authorization** -- Mutations on shared resources check `created_by_user_id` or admin role.
