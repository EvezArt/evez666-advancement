#!/bin/bash
# Quantum-Evez CLI Wrapper
# Usage: ./quantum_ez.py <command> [args]

cd /root/.openclaw/workspace/skills/quantum-ez
exec python3 quantum_ez.py "$@"