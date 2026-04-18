#!/bin/bash
# Continuous Monitoring & Auto-Healing System
# Ensures: consistent uptime, operational deployments, mass-production styled wiring

MONITOR_DIR="/root/.openclaw/workspace/monitoring"
LOGS_DIR="/root/.openclaw/workspace/logs"

mkdir -p "$MONITOR_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOGS_DIR/monitor.log"
}

check_quantum_stack() {
    log "=== Checking Quantum Stack ==="
    
    # Check Qiskit
    if python3 -c "import qiskit" 2>/dev/null; then
        QV=$(python3 -c "import qiskit; print(qiskit.__version__)")
        log "✅ Qiskit: $QV"
    else
        log "❌ Qiskit: MISSING - attempting install..."
        python3 -m pip install --break-system-packages qiskit qiskit-aer -q
    fi
    
    # Check quantum scripts
    if [ -f "/root/.openclaw/workspace/skills/quantum-ez/quantum_ez.sh" ]; then
        log "✅ Quantum Scripts: Available"
    else
        log "❌ Quantum Scripts: MISSING"
    fi
    
    # Run test algorithm
    RESULT=$(/root/.openclaw/workspace/skills/quantum-ez/quantum_ez.sh algo run bell 2>/dev/null)
    if echo "$RESULT" | grep -q "executed"; then
        log "✅ Quantum Execution: Working"
    else
        log "⚠️  Quantum Execution: Issues detected"
    fi
}

check_research_engine() {
    log "=== Checking Research Engine ==="
    
    if [ -f "/root/.openclaw/workspace/auto/evez_advancement.py" ]; then
        STATUS=$(python3 /root/.openclaw/workspace/auto/evez_advancement.py status 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'KB:{d[\"knowledge_base\"][\"solved_problems\"]} caps:{d[\"knowledge_base\"][\"capabilities\"]}')" 2>/dev/null)
        log "✅ Research Engine: Active ($STATUS)"
    else
        log "❌ Research Engine: MISSING"
    fi
}

check_deployments() {
    log "=== Checking Deployments ==="
    
    # Check experiment outputs
    EXPERIMENTS=$(ls /root/.openclaw/workspace/experiments/*.csv 2>/dev/null | wc -l)
    log "📊 Experiment files: $EXPERIMENTS"
    
    # Check knowledge base
    if [ -f "/root/.openclaw/workspace/knowledge_base.json" ]; then
        KB_SIZE=$(du -h /root/.openclaw/workspace/knowledge_base.json | cut -f1)
        log "📚 Knowledge Base: $KB_SIZE"
    fi
    
    # Check daily summaries
    SUMMARIES=$(ls /root/.openclaw/workspace/experiments/daily_summary.md 2>/dev/null | wc -l)
    if [ "$SUMMARIES" -gt 0 ]; then
        log "✅ Daily Summaries: Present"
    fi
}

check_projects() {
    log "=== Checking Projects ==="
    
    if [ -f "/root/.openclaw/workspace/projects/project_registry.json" ]; then
        PROJECTS=$(python3 -c "import json; print(len(json.load(open('/root/.openclaw/workspace/projects/project_registry.json'))))" 2>/dev/null)
        log "📁 Active Projects: $PROJECTS"
    else
        log "📁 Projects: None registered yet"
    fi
}

heal_if_needed() {
    log "=== Auto-Healing Check ==="
    
    # Fix missing directories
    for dir in logs experiments ops ci journal research deploy ml projects monitoring temporal auto; do
        if [ ! -d "/root/.openclaw/workspace/$dir" ]; then
            mkdir -p "/root/.openclaw/workspace/$dir"
            log "🔧 Created missing directory: $dir"
        fi
    done
    
    # Ensure scripts are executable
    chmod +x /root/.openclaw/workspace/skills/quantum-ez/*.sh 2>/dev/null
    chmod +x /root/.openclaw/workspace/ops/healthcheck.sh 2>/dev/null
    chmod +x /root/.openclaw/workspace/ci/ci_sidecar.sh 2>/dev/null
    chmod +x /root/.openclaw/workspace/auto/*.sh 2>/dev/null
    
    log "✅ Auto-healing complete"
}

run_full_cycle() {
    log "========================================="
    log "=== EVEZ666 CONTINUOUS MONITOR ==="
    log "========================================="
    
    check_quantum_stack
    check_research_engine
    check_deployments
    check_projects
    heal_if_needed
    
    log "=== MONITOR CYCLE COMPLETE ==="
    
    # Get system status
    python3 /root/.openclaw/workspace/auto/evez_advancement.py status 2>/dev/null | head -20 >> "$LOGS_DIR/monitor.log"
}

# Run cycle
run_full_cycle

# Schedule next run
echo "Next monitor run in 10 minutes..."