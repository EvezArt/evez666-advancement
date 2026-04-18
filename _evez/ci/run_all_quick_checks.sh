#!/bin/bash
# Consolidated CI Quick Check Runner
# Runs all EVeZ repo quick checks

WORKSPACE="/root/.openclaw/workspace"
EVEZ_DIR="$WORKSPACE/_evez"
LOG_FILE="$EVEZ_DIR/logs/ci/quick_status.log"

mkdir -p "$EVEZ_DIR/logs/ci"

echo "=== EVEZ CI QUICK CHECKS ===" | tee -a "$LOG_FILE"
echo "Timestamp: $(date -Iseconds)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

REPOS="evez-os evez-vcl evez-sim evez666-arg-canon evez-agentnet evez-platform nexus evez-autonomous-ledger maes lord-evez agentvault Evez666"

PASS=0
FAIL=0

for repo in $REPOS; do
    if [ -f "$EVEZ_DIR/ci/quick_status_${repo}.json" ]; then
        STATUS=$(python3 -c "import json; d=json.load(open('$EVEZ_DIR/ci/quick_status_${repo}.json')); print('PASS' if d.get('pass',False) else 'FAIL')")
        if [ "$STATUS" = "PASS" ]; then
            ((PASS++))
            echo "✓ $repo" | tee -a "$LOG_FILE"
        else
            ((FAIL++))
            echo "✗ $repo" | tee -a "$LOG_FILE"
        fi
    else
        echo "? $repo (no status file)" | tee -a "$LOG_FILE"
    fi
done

echo "" | tee -a "$LOG_FILE"
echo "Results: $PASS passed, $FAIL failed" | tee -a "$LOG_FILE"
echo "=== END ===" | tee -a "$LOG_FILE"