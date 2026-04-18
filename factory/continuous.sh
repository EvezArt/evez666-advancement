#!/bin/bash
# Continuous Factory Runner - keeps the factory running forever
# Usage: ./continuous_factory.sh [cycles] [interval]

CYCLES=${1:-1000}
INTERVAL=${2:-5}

echo "=== STARTING CONTINUOUS EVEZ666 FACTORY ==="
echo "Cycles: $CYCLES, Interval: ${INTERVAL}s"

cd /root/.openclaw/workspace/factory

for i in $(seq 1 $CYCLES); do
    echo "=== Factory Cycle $i ==="
    python3 factory_orchestrator.py start 1 2>&1 | tail -15
    echo "Sleeping ${INTERVAL}s..."
    sleep $INTERVAL
done