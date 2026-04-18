#!/usr/bin/env python3
"""
EVEZ MULTI-AGENT ORCHESTRATOR v2 - Runs agents as background processes
"""

import os
import json
import time
import subprocess
from datetime import datetime
from pathlib import Path

AGENTS_DIR = "/root/.openclaw/workspace/agents"
STATE_FILE = f"{AGENTS_DIR}/orchestrator_state.json"
LOG_FILE = f"{AGENTS_DIR}/orchestrator.log"

# Updated agent specs - now using standalone scripts
AGENT_SPECS = {
    "quantum_runner": {
        "description": "Execute quantum algorithms continuously",
        "command": f"nohup python3 {AGENTS_DIR}/quantum_runner.py > {AGENTS_DIR}/quantum_runner.log 2>&1 &",
        "enabled": True
    },
    "wealth_hunter": {
        "description": "Scan for deals, crypto, loopholes",
        "command": f"nohup python3 {AGENTS_DIR}/wealth_hunter.py > {AGENTS_DIR}/wealth_hunter.log 2>&1 &",
        "enabled": True
    },
    "ci_watcher": {
        "description": "Monitor CI across all repos",
        "command": f"nohup python3 {AGENTS_DIR}/ci_watcher.py > {AGENTS_DIR}/ci_watcher.log 2>&1 &",
        "enabled": True
    }
}

def log(msg):
    timestamp = datetime.now().isoformat()
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def spawn_agent(name, spec):
    """Start an agent as background process"""
    try:
        # Use shell=True for nohup commands
        subprocess.run(spec["command"], shell=True, check=False)
        log(f"SPAWNED: {name}")
        return True
    except Exception as e:
        log(f"FAILED: {name} - {e}")
        return False

def check_agents():
    """Check which agents are running"""
    running = {}
    
    # Check processes
    result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
    for line in result.stdout.split("\n"):
        if "quantum_runner.py" in line and "nohup" not in line:
            running["quantum_runner"] = True
        elif "wealth_hunter.py" in line and "nohup" not in line:
            running["wealth_hunter"] = True
        elif "ci_watcher.py" in line and "nohup" not in line:
            running["ci_watcher"] = True
    
    return running

def main():
    log("=== MULTI-AGENT ORCHESTRATOR v2 STARTED ===")
    
    # Spawn all agents
    for name, spec in AGENT_SPECS.items():
        if spec.get("enabled", True):
            spawn_agent(name, spec)
    
    # Monitor loop
    cycle = 0
    while True:
        cycle += 1
        time.sleep(30)  # Check every 30 seconds
        
        running = check_agents()
        
        # Ensure all enabled agents are running
        for name, spec in AGENT_SPECS.items():
            if spec.get("enabled", True) and name not in running:
                log(f"RESTARTING: {name}")
                spawn_agent(name, spec)
        
        log(f"CYCLE {cycle}: {len(running)} agents running")

if __name__ == "__main__":
    main()