#!/bin/bash
# Automated backup script for Open WebUI production deployment

set -e

# Configuration
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=${BACKUP_RETENTION_DAYS:-30}

# Logging
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

log "Starting backup process..."

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup PostgreSQL database
log "Backing up PostgreSQL database..."
pg_dump -h db -U "$POSTGRES_USER" -d "$POSTGRES_DB" > "$BACKUP_DIR/postgres_backup_$DATE.sql"
gzip "$BACKUP_DIR/postgres_backup_$DATE.sql"

# Backup Redis data (if needed)
log "Backing up Redis data..."
redis-cli -h redis --rdb "$BACKUP_DIR/redis_backup_$DATE.rdb"

# Backup Open WebUI data directory
log "Backing up Open WebUI data..."
tar -czf "$BACKUP_DIR/openwebui_data_$DATE.tar.gz" -C /app/backend data/

# Backup Ollama models
log "Backing up Ollama models..."
tar -czf "$BACKUP_DIR/ollama_models_$DATE.tar.gz" -C /root/.ollama models/

# Clean up old backups
log "Cleaning up backups older than $RETENTION_DAYS days..."
find "$BACKUP_DIR" -type f -name "*.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -type f -name "*.sql" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -type f -name "*.rdb" -mtime +$RETENTION_DAYS -delete

# Create backup summary
BACKUP_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
BACKUP_COUNT=$(find "$BACKUP_DIR" -type f | wc -l)

log "Backup completed successfully!"
log "Total backup size: $BACKUP_SIZE"
log "Number of backup files: $BACKUP_COUNT"
