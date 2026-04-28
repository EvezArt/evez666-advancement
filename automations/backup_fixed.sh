#!/bin/bash
# EVEZ KiloClaw Backup - FIXED with direct exec + rclone
set -e

BACKUP_DIR="/root/.openclaw/workspace"
DEST="/root/.openclaw/backups"
LOG="$DEST/backup.log"
TIMESTAMP=$(date '+%Y-%m-%d_%H-%M-%S')

mkdir -p "$DEST"

echo "[$TIMESTAMP] === Backup started ===" >> "$LOG"

# Archive critical files
ARCHIVE="/tmp/kiloclaw_backup_${TIMESTAMP}.tar.gz"
tar -czf "$ARCHIVE" \
    "$BACKUP_DIR/openclaw.json" \
    "$BACKUP_DIR/SOUL.md" \
    "$BACKUP_DIR/USER.md" \
    "$BACKUP_DIR/MEMORY.md" \
    "$BACKUP_DIR/AGENTS.md" \
    "$BACKUP_DIR/TOOLS.md" \
    "$BACKUP_DIR/cron/jobs.json" \
    "$BACKUP_DIR/workspace/memory" \
    "$BACKUP_DIR/workspace/money" \
    2>/dev/null || true

if [ -f "$ARCHIVE" ]; then
    SIZE=$(du -h "$ARCHIVE" | cut -f1)
    echo "[$TIMESTAMP] Archive created: $ARCHIVE ($SIZE)" >> "$LOG"
    
    # Move to backup directory
    cp "$ARCHIVE" "$DEST/kiloclaw_backup_${TIMESTAMP}.tar.gz"
    rm "$ARCHIVE"
    
    # Keep last 7 backups
    cd "$DEST"
    ls -t kiloclaw_backup_*.tar.gz 2>/dev/null | tail -n +8 | xargs -r rm
    
    echo "[$TIMESTAMP] Backup complete: $SIZE" >> "$LOG"
    echo "[$TIMESTAMP] Files backed up: $(ls -1 $DEST/kiloclaw_backup_*.tar.gz | wc -l) total archives" >> "$LOG"
else
    echo "[$TIMESTAMP] Backup FAILED - no archive created" >> "$LOG"
    exit 1
fi