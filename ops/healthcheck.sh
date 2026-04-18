#!/bin/bash
# Healthcheck Script - Monitors disk, CPU, memory, and critical services
# Run manually: ./healthcheck.sh
# Or schedule with: while true; do ./healthcheck.sh; sleep 600; done

LOG_DIR="/root/.openclaw/workspace/ops"
LOG_DIR="${LOG_DIR}"
mkdir -p "$LOG_DIR"

LOG_FILE="$LOG_DIR/health.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Thresholds
DISK_THRESHOLD=90
CPU_THRESHOLD=80
MEM_THRESHOLD=80

log() {
    echo "[$TIMESTAMP] $1" | tee -a "$LOG_FILE"
}

check_disk() {
    USAGE=$(df -h / | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ "$USAGE" -gt "$DISK_THRESHOLD" ]; then
        log "⚠️  DISK WARNING: ${USAGE}% used (threshold: ${DISK_THRESHOLD}%)"
        return 1
    else
        log "✅ DISK OK: ${USAGE}% used"
        return 0
    fi
}

check_cpu() {
    # Get CPU usage (simple method)
    CPU=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')
    CPU_INT=${CPU%.*}
    
    if [ "$CPU_INT" -gt "$CPU_THRESHOLD" ]; then
        log "⚠️  CPU WARNING: ${CPU}% used (threshold: ${CPU_THRESHOLD}%)"
        return 1
    else
        log "✅ CPU OK: ${CPU}% used"
        return 0
    fi
}

check_memory() {
    MEM=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100}')
    
    if [ "$MEM" -gt "$MEM_THRESHOLD" ]; then
        log "⚠️  MEMORY WARNING: ${MEM}% used (threshold: ${MEM_THRESHOLD}%)"
        return 1
    else
        log "✅ MEMORY OK: ${MEM}% used"
        return 0
    fi
}

check_services() {
    log "=== Service Status ==="
    
    # Check OpenClaw (gateway process)
    if pgrep -x "openclaw" > /dev/null 2>&1; then
        log "✅ OpenClaw: Running"
    else
        log "❌ OpenClaw: NOT RUNNING"
    fi
    
    # Check Node
    if pgrep -x "node" > /dev/null 2>&1; then
        log "✅ Node: Running"
    else
        log "❌ Node: NOT RUNNING"
    fi
    
    # Check Python (quantum scripts)
    if pgrep -f "quantum_ez" > /dev/null 2>&1; then
        log "✅ Quantum Scripts: Running"
    else
        log "⚠️  Quantum Scripts: Idle"
    fi
}

check_quantum_stack() {
    log "=== Quantum Stack ==="
    
    # Check Qiskit
    if python3 -c "import qiskit" 2>/dev/null; then
        QISKIT_VERSION=$(python3 -c "import qiskit; print(qiskit.__version__)" 2>/dev/null)
        log "✅ Qiskit: $QISKIT_VERSION"
    else
        log "❌ Qiskit: NOT INSTALLED"
    fi
    
    # Check state files
    STATE_FILES=$(ls /root/.openclaw/workspace/state/quantum/*.json 2>/dev/null | wc -l)
    if [ "$STATE_FILES" -gt 0 ]; then
        log "✅ Quantum State: $STATE_FILES files"
    else
        log "⚠️  Quantum State: No state files"
    fi
}

run_healthcheck() {
    log "========================================="
    log "=== HEALTHCHECK STARTED"
    log "========================================="
    
    ISSUES=0
    
    check_disk || ((ISSUES++))
    check_cpu || ((ISSUES++))
    check_memory || ((ISSUES++))
    check_services
    check_quantum_stack
    
    log "========================================="
    if [ "$ISSUES" -gt 0 ]; then
        log "⚠️  HEALTHCHECK COMPLETED: $ISSUES issue(s) found"
    else
        log "✅ HEALTHCHECK COMPLETED: All OK"
    fi
    log "========================================="
    
    return $ISSUES
}

# Run the check
run_healthcheck
exit $?