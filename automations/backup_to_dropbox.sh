#!/bin/bash
#
# Backup automation script - uploads critical files to Dropbox
# Uses mcporter to call Composio tools
#

set -e

# Configuration
LOG_FILE="/root/.openclaw/workspace/logs/backup.log"
MCPORTER_CONFIG="/root/.openclaw/workspace/config/mcporter.json"
DROPBOX_FOLDER="KiloClaw_Backups"

# Files to backup
BACKUP_FILES=(
    "/root/.openclaw/openclaw.json"
    "/root/.openclaw/cron/jobs.json"
    "/root/.openclaw/workspace/memory/2026-04-18.md"
    "/root/.openclaw/workspace/memory/2026-04-19.md"
    "/root/.openclaw/workspace/factory/cycle_log.json"
)

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Error handler
error_exit() {
    log "ERROR: $1"
    exit 1
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check mcporter config exists
    if [ ! -f "$MCPORTER_CONFIG" ]; then
        error_exit "mcporter config not found at $MCPORTER_CONFIG"
    fi
    
    # Check backup files exist
    for file in "${BACKUP_FILES[@]}"; do
        if [ ! -f "$file" ]; then
            log "WARNING: Backup file not found: $file"
        else
            log "Found: $file ($(wc -c < "$file") bytes)"
        fi
    done
}

# List current backups on Google Drive (for reference)
list_google_drive_backups() {
    log "Checking Google Drive for existing backups..."
    
    # Note: This would use mcporter to call GOOGLEDRIVE_LIST_FILES
    # For now, we'll log that this step would run
    log "Google Drive check: Would call GOOGLEDRIVE_LIST_FILES"
    log "Google Drive integration available for reference only in this backup"
}

# Upload a single file to Dropbox
upload_to_dropbox() {
    local file_path="$1"
    local file_name=$(basename "$file_path")
    
    if [ ! -f "$file_path" ]; then
        log "SKIP: File not found: $file_path"
        return 1
    fi
    
    log "Uploading $file_name to Dropbox..."
    
    local timestamp=$(date '+%Y-%m-%d_%H-%M-%S')
    local backup_name="${timestamp}_${file_name}"
    
    # Execute via mcporter call composio.COMPOSIO_EXECUTE_TOOL
    # Using the correct syntax for Composio MCP
    local result
    result=$(mcporter call composio.COMPOSIO_EXECUTE_TOOL \
        tool="dropbox_upload_file" \
        path="${DROPBOX_FOLDER}/${backup_name}" \
        content=@"$file_path" 2>&1) || {
        log "WARNING: Failed to upload $file_name: $result"
        return 1
    }
    
    if echo "$result" | grep -qE "error|Error|failed"; then
        log "WARNING: Upload may have failed for $file_name: $result"
        return 1
    fi
    
    log "SUCCESS: Uploaded $file_name -> ${DROPBOX_FOLDER}/${backup_name}"
    return 0
}

# Main backup function
run_backup() {
    log "=== Starting Dropbox Backup ==="
    log "Backup folder: $DROPBOX_FOLDER"
    
    # Check prerequisites
    check_prerequisites
    
    # List current Google Drive backups (informational)
    list_google_drive_backups
    
    # Upload each file
    local success_count=0
    local fail_count=0
    
    for file in "${BACKUP_FILES[@]}"; do
        if [ -f "$file" ]; then
            if upload_to_dropbox "$file"; then
                ((success_count++))
            else
                ((fail_count++))
            fi
        else
            ((fail_count++))
        fi
    done
    
    log "=== Backup Complete ==="
    log "Successful: $success_count, Failed: $fail_count"
    
    if [ $fail_count -gt 0 ]; then
        log "WARNING: Some files failed to backup"
        return 1
    fi
    
    log "All files backed up successfully!"
    return 0
}

# Run the backup
run_backup