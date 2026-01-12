#!/bin/bash
################################################################################
# Database Backup Script for Resume Enhancement Tool
#
# This script performs automated backups of the PostgreSQL database
# and implements a retention policy to manage backup storage.
#
# Usage:
#   ./scripts/backup.sh
#
# Schedule with cron (daily at 2 AM):
#   0 2 * * * /path/to/resume-enhancement-tool/scripts/backup.sh >> /var/log/backup.log 2>&1
#
################################################################################

set -e  # Exit on error
set -u  # Exit on undefined variable
set -o pipefail  # Exit on pipe failure

# Configuration
BACKUP_DIR="${BACKUP_DIR:-/var/backups/resume-tool}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="backup_${DATE}.sql.gz"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if DATABASE_URL is set
if [ -z "${DATABASE_URL:-}" ]; then
    log_error "DATABASE_URL environment variable is not set"
    log_error "Please set it in your .env file or export it before running this script"
    exit 1
fi

# Create backup directory if it doesn't exist
if [ ! -d "$BACKUP_DIR" ]; then
    log_info "Creating backup directory: $BACKUP_DIR"
    mkdir -p "$BACKUP_DIR"
fi

# Check if pg_dump is available
if ! command -v pg_dump &> /dev/null; then
    log_error "pg_dump command not found. Please install PostgreSQL client tools."
    exit 1
fi

# Perform backup
log_info "Starting database backup..."
log_info "Backup file: $BACKUP_FILE"

if pg_dump "$DATABASE_URL" | gzip > "$BACKUP_DIR/$BACKUP_FILE"; then
    # Get backup file size
    BACKUP_SIZE=$(du -h "$BACKUP_DIR/$BACKUP_FILE" | cut -f1)
    log_info "Backup completed successfully: $BACKUP_FILE ($BACKUP_SIZE)"
else
    log_error "Backup failed!"
    exit 1
fi

# Delete old backups
log_info "Cleaning up old backups (retention: $RETENTION_DAYS days)..."
DELETED_COUNT=$(find "$BACKUP_DIR" -name "backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete -print | wc -l)

if [ "$DELETED_COUNT" -gt 0 ]; then
    log_info "Deleted $DELETED_COUNT old backup(s)"
else
    log_info "No old backups to delete"
fi

# Display backup summary
log_info "==================== Backup Summary ===================="
log_info "Backup directory: $BACKUP_DIR"
log_info "Total backups: $(ls -1 $BACKUP_DIR/backup_*.sql.gz 2>/dev/null | wc -l)"
log_info "Disk usage: $(du -sh $BACKUP_DIR | cut -f1)"
log_info "Oldest backup: $(ls -1t $BACKUP_DIR/backup_*.sql.gz 2>/dev/null | tail -1 | xargs basename)"
log_info "Newest backup: $(ls -1t $BACKUP_DIR/backup_*.sql.gz 2>/dev/null | head -1 | xargs basename)"
log_info "========================================================"

# Check disk space warning
AVAILABLE_SPACE_MB=$(df -m "$BACKUP_DIR" | awk 'NR==2 {print $4}')
if [ "$AVAILABLE_SPACE_MB" -lt 1024 ]; then
    log_warn "Low disk space warning: Only ${AVAILABLE_SPACE_MB}MB available"
fi

log_info "Backup process completed"
exit 0
