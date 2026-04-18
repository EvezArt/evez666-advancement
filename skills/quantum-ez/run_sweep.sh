#!/bin/bash
# Quantum-Eez Runner - Parameter Sweep Launcher
# Usage: ./run_sweep.sh [sweep|summary|status]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$SCRIPT_DIR"

case "$1" in
    sweep)
        python3 quantum_ez_runner.py sweep
        ;;
    summary)
        python3 quantum_ez_runner.py summary
        ;;
    status)
        python3 quantum_ez_runner.py status
        ;;
    *)
        echo "Usage: $0 {sweep|summary|status}"
        exit 1
        ;;
esac