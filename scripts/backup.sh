#!/usr/bin/env bash
#
# Database backup script for Pretorin CRM (PostgreSQL).
#
# Usage:
#   ./scripts/backup.sh                     # Backup using defaults
#   ./scripts/backup.sh /path/to/backups    # Backup to custom directory
#
# Restore:
#   gunzip -c backups/crm_2026-03-09_120000.sql.gz | \
#     docker compose exec -T db psql -U crm -d crm
#
#   Or without Docker:
#     gunzip -c backups/crm_2026-03-09_120000.sql.gz | psql "$DATABASE_URL"
#
# Environment variables:
#   DATABASE_URL  - PostgreSQL connection string (default: from .env or docker)
#   BACKUP_DIR    - Directory to store backups (default: ./backups or $1)
#   RETAIN_DAYS   - Number of days to keep old backups (default: 30)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Load environment
if [ -f "$PROJECT_ROOT/.env" ]; then
    set -a
    source "$PROJECT_ROOT/.env"
    set +a
fi

BACKUP_DIR="${1:-${BACKUP_DIR:-$PROJECT_ROOT/backups}}"
RETAIN_DAYS="${RETAIN_DAYS:-30}"
TIMESTAMP="$(date +%Y-%m-%d_%H%M%S)"
BACKUP_FILE="$BACKUP_DIR/crm_${TIMESTAMP}.sql.gz"

mkdir -p "$BACKUP_DIR"

echo "Starting backup at $(date)"

# Try Docker first, fall back to direct pg_dump
if docker compose -f "$PROJECT_ROOT/docker-compose.yml" ps db --status running -q 2>/dev/null | grep -q .; then
    echo "Using Docker Compose db container..."
    docker compose -f "$PROJECT_ROOT/docker-compose.yml" exec -T db \
        pg_dump -U crm --clean --if-exists --no-owner crm | gzip > "$BACKUP_FILE"
elif [ -n "${DATABASE_URL:-}" ]; then
    echo "Using DATABASE_URL..."
    pg_dump --clean --if-exists --no-owner "$DATABASE_URL" | gzip > "$BACKUP_FILE"
else
    echo "ERROR: No running Docker db container and DATABASE_URL not set." >&2
    exit 1
fi

FILESIZE=$(du -h "$BACKUP_FILE" | cut -f1)
echo "Backup saved: $BACKUP_FILE ($FILESIZE)"

# Prune old backups
if [ "$RETAIN_DAYS" -gt 0 ]; then
    PRUNED=$(find "$BACKUP_DIR" -name "crm_*.sql.gz" -mtime +"$RETAIN_DAYS" -print -delete | wc -l)
    if [ "$PRUNED" -gt 0 ]; then
        echo "Pruned $PRUNED backup(s) older than $RETAIN_DAYS days"
    fi
fi

echo "Backup complete at $(date)"
