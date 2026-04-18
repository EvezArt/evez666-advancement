#!/bin/bash
# Continuous Factory - NEVER STOPS
# Usage: ./start_forever.sh [max_cycles]

MAX_CYCLES=${1:-10000}

echo "=== EVEZ666 CONTINUOUS FACTORY STARTING ==="
echo "Max cycles: $MAX_CYCLES"
echo "Repos: evez-os, evez-agentnet, evez-platform, evez-vcl, nexus, Evez666, etc."

cd /root/.openclaw/workspace/factory

python3 continuous_factory.py forever $MAX_CYCLES