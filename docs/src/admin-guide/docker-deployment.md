# Docker Deployment

Pretorin CRM ships with Docker Compose for production-like deployment.

## Prerequisites

- Docker Engine 20+
- Docker Compose v2+

## Quick Deploy

```bash
git clone https://github.com/pretorin/simple-crm.git
cd simple-crm

# Configure environment variables in docker-compose.yml or use .env
# At minimum, change SECRET_KEY and database credentials

docker compose up -d
```

The services start on:

| Service | Port | URL |
|---------|------|-----|
| Frontend | 3000 | `http://localhost:3000` |
| Backend | 8000 | `http://localhost:8000` |
| PostgreSQL | 5432 | Internal only |

## Services

### PostgreSQL (db)

- Image: `postgres:16-alpine`
- Default credentials: user `crm`, password `crm`, database `crm`
- Data persisted in a Docker volume (`pgdata`)
- Health check runs every 5 seconds

### Backend

- Built from `backend/Dockerfile` (Python 3.12-slim)
- Depends on PostgreSQL (waits for health check)
- Resource limits: 1 CPU, 1GB memory
- Environment variables configured in `docker-compose.yml`

### Frontend

- Built from `frontend/Dockerfile` (multi-stage: Node build, then Nginx serve)
- Depends on backend (waits for health check)
- Nginx serves the built React app and proxies API requests

## Configuration

Edit the `docker-compose.yml` environment section or use a `.env` file:

```yaml
environment:
  - DATABASE_URL=postgresql://crm:crm@db:5432/crm
  - SECRET_KEY=your-production-secret-key
  - ENV=production
  - FRONTEND_URL=https://your-domain.com
  - GOOGLE_CLIENT_ID=your-client-id
  - GOOGLE_CLIENT_SECRET=your-client-secret
```

## Updating

```bash
git pull
docker compose build
docker compose up -d
```

## Data Persistence

PostgreSQL data is stored in the `pgdata` Docker volume. To back up:

```bash
docker compose exec db pg_dump -U crm crm > backup.sql
```

To restore:

```bash
docker compose exec -T db psql -U crm crm < backup.sql
```

## Troubleshooting

### Backend won't start

Check logs:

```bash
docker compose logs backend
```

Common issues:
- `SECRET_KEY` not set
- Database connection refused (PostgreSQL not ready yet -- Docker Compose should handle this with health checks)

### Frontend returns 502

The backend may not be healthy yet. Check:

```bash
docker compose ps
docker compose logs backend
```
