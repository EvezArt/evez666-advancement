#!/bin/bash
# CI Sidecar - Quick status checker and watcher
# Usage: ./ci_sidecar.sh <repo_path> [status|watch|fix]

REPO_PATH="${1:-.}"
CI_DIR="$REPO_PATH/ci"
LOG_DIR="/root/.openclaw/workspace/logs"

mkdir -p "$CI_DIR"
mkdir -p "$LOG_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_DIR/ci_sidecar.log"
}

get_quick_status() {
    log "=== Running Quick CI Check on $REPO_PATH ==="
    
    STATUS_FILE="$CI_DIR/quick_status.json"
    
    # Check if git repo
    if [ ! -d "$REPO_PATH/.git" ]; then
        echo '{"status":"error","message":"Not a git repository","pass":false}' > "$STATUS_FILE"
        log "❌ Not a git repository"
        return 1
    fi
    
    START_TIME=$(date +%s)
    
    # Quick lint checks (if tools available)
    ISSUES=0
    FAILING_FILES=""
    
    # Check for common issues
    if command -v pylint &> /dev/null; then
        if pylint "$REPO_PATH" 2>/dev/null | grep -q "error"; then
            ((ISSUES++))
            FAILING_FILES="${FAILING_FILES}pylint-errors,"
        fi
    fi
    
    if command -v flake8 &> /dev/null; then
        if flake8 "$REPO_PATH" --count 2>/dev/null | grep -q "[1-9]"; then
            ((ISSUES++))
            FAILING_FILES="${FAILING_FILES}flake8,"
        fi
    fi
    
    # Check for uncommitted changes
    cd "$REPO_PATH"
    if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
        log "📝 Uncommitted changes detected"
    fi
    
    # Check last commit
    LAST_COMMIT=$(git log -1 --format="%h %s" 2>/dev/null | head -1)
    log "📌 Last commit: $LAST_COMMIT"
    
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    
    # Write status
    if [ "$ISSUES" -eq 0 ]; then
        echo "{\"status\":\"pass\",\"pass\":true,\"issues\":0,\"duration\":$DURATION,\"last_commit\":\"$LAST_COMMIT\"}" > "$STATUS_FILE"
        log "✅ Quick check PASSED (${DURATION}s)"
    else
        echo "{\"status\":\"fail\",\"pass\":false,\"issues\":$ISSUES,\"failing_files\":\"$FAILING_FILES\",\"duration\":$DURATION,\"last_commit\":\"$LAST_COMMIT\"}" > "$STATUS_FILE"
        log "❌ Quick check FAILED: $ISSUES issues"
    fi
    
    cat "$STATUS_FILE"
}

watch_repo() {
    log "=== Starting Repo Watcher for $REPO_PATH ==="
    LAST_COMMIT=""
    
    while true; do
        cd "$REPO_PATH"
        
        CURRENT_COMMIT=$(git log -1 --format="%h" 2>/dev/null | head -1)
        
        if [ "$CURRENT_COMMIT" != "$LAST_COMMIT" ] && [ -n "$CURRENT_COMMIT" ]; then
            log "📥 New commit detected: $CURRENT_COMMIT"
            get_quick_status
            LAST_COMMIT="$CURRENT_COMMIT"
        fi
        
        sleep 3600  # Check every hour
    done
}

suggest_fix() {
    log "=== Generating Suggested Fix ==="
    
    FIX_FILE="$CI_DIR/suggested_fix_$(date +%Y%m%d).patch"
    
    cd "$REPO_PATH"
    
    # Get recent diff
    git diff HEAD~1 HEAD > "$FIX_FILE" 2>/dev/null
    
    if [ -s "$FIX_FILE" ]; then
        log "📄 Fix patch written to $FIX_FILE"
        echo "=== Suggested Fix ===" 
        head -20 "$FIX_FILE"
    else
        log "❌ No changes to create patch"
        echo '{"error":"No recent changes to analyze"}' > "$FIX_FILE"
    fi
}

case "$2" in
    status)
        get_quick_status
        ;;
    watch)
        watch_repo
        ;;
    fix)
        suggest_fix
        ;;
    *)
        echo "Usage: $0 <repo_path> {status|watch|fix}"
        echo "Example: $0 /root/.openclaw/workspace status"
        ;;
esac