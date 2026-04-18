#!/usr/bin/env python3
"""
EVEZ MULTI-AGENT ORCHESTRATOR - Never stops, keeps agents running
Each agent has a purpose, monitors health, respawns on failure
"""

import os
import json
import time
import subprocess
import signal
from datetime import datetime
from pathlib import Path

AGENTS_DIR = "/root/.openclaw/workspace/agents"
STATE_FILE = f"{AGENTS_DIR}/orchestrator_state.json"
LOG_FILE = f"{AGENTS_DIR}/orchestrator.log"

os.makedirs(AGENTS_DIR, exist_ok=True)

# Define agents with their tasks
AGENT_SPECS = {
    "quantum_runner": {
        "description": "Execute quantum algorithms continuously",
        "command": "python3 /root/.openclaw/workspace/skills/quantum-ez/quantum_ez_runner.py",
        "timeout": 60,
        "restart_delay": 5,
        "enabled": True
    },
    "wealth_hunter": {
        "description": "Scan for deals, crypto, loopholes",
        "command": "python3 /root/.openclaw/workspace/money_machine/wealth.py",
        "timeout": 120,
        "restart_delay": 10,
        "enabled": True
    },
    "ci_watcher": {
        "description": "Monitor CI across all repos",
        "command": "bash /root/.openclaw/workspace/factory/ci_sidecar.sh",
        "timeout": 300,
        "restart_delay": 15,
        "enabled": True
    },
    "model_trainer": {
        "description": "Train EVEZ-X model continuously",
        "command": "python3 /root/.openclaw/workspace/ml/evez_omni.py",
        "timeout": 180,
        "restart_delay": 10,
        "enabled": True
    },
    "reasoning_pipeline": {
        "description": "Run reasoning pipeline cycles",
        "command": "python3 /root/.openclaw/workspace/pipeline/reasoning_pipeline.py",
        "timeout": 120,
        "restart_delay": 5,
        "enabled": True
    }
}

class AgentOrchestrator:
    def __init__(self):
        self.running_agents = {}  # pid -> spec
        self.load_state()
        
    def load_state(self):
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE) as f:
                self.state = json.load(f)
        else:
            self.state = {"start_time": datetime.now().isoformat(), "cycles": 0}
    
    def save_state(self):
        with open(STATE_FILE, "w") as f:
            json.dump(self.state, f, indent=2)
    
    def log(self, msg):
        timestamp = datetime.now().isoformat()
        line = f"[{timestamp}] {msg}"
        print(line)
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    
    def spawn_agent(self, name, spec):
        """Start an agent process"""
        try:
            # Start process
            proc = subprocess.Popen(
                spec["command"].split(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True
            )
            
            self.running_agents[proc.pid] = {
                "name": name,
                "spec": spec,
                "started": datetime.now().isoformat(),
                "restarts": 0
            }
            
            self.log(f"SPAWNED: {name} (pid={proc.pid})")
            return proc
            
        except Exception as e:
            self.log(f"FAILED to spawn {name}: {e}")
            return None
    
    def check_agent_health(self, pid, name, spec):
        """Check if agent is still running"""
        try:
            # Check if process exists
            os.kill(pid, 0)  # Signal 0 just checks existence
            return True
        except OSError:
            # Process dead - check restart count
            agent_state = self.running_agents.get(pid, {})
            restarts = agent_state.get("restarts", 0)
            
            if restarts < 5:  # Max 5 restarts
                self.log(f"AGENT DIED: {name} (pid={pid}), restarting...")
                time.sleep(spec.get("restart_delay", 5))
                return False  # Signal need to restart
            else:
                self.log(f"AGENT FAILED: {name} exceeded max restarts")
                return None  # Permanent failure
    
    def run_cycle(self):
        """One cycle of orchestration"""
        self.state["cycles"] += 1
        cycle = self.state["cycles"]
        
        self.log(f"=== CYCLE {cycle} ===")
        
        # Check and maintain each agent
        for name, spec in AGENT_SPECS.items():
            if not spec.get("enabled", True):
                continue
            
            found = False
            for pid, agent_info in list(self.running_agents.items()):
                if agent_info["name"] == name:
                    found = True
                    # Check health
                    alive = self.check_agent_health(pid, name, spec)
                    if alive:
                        self.log(f"HEALTHY: {name} (pid={pid})")
                    else:
                        # Need to restart
                        del self.running_agents[pid]
                        self.spawn_agent(name, spec)
                    break
            
            if not found:
                # Not running - spawn it
                self.spawn_agent(name, spec)
        
        self.save_state()
        return len(self.running_agents)
    
    def run_forever(self):
        """Never stop - run cycles"""
        self.log("=== ORCHESTRATOR STARTED ===")
        
        # Initial spawn
        for name, spec in AGENT_SPECS.items():
            if spec.get("enabled", True):
                self.spawn_agent(name, spec)
        
        # Run cycles forever
        while True:
            try:
                count = self.run_cycle()
                self.log(f"Cycle complete: {count} agents running")
                
                # Short sleep between cycles
                time.sleep(10)
                
            except KeyboardInterrupt:
                self.log("STOPPED by user")
                break
            except Exception as e:
                self.log(f"CYCLE ERROR: {e}")
                time.sleep(5)

if __name__ == "__main__":
    orch = AgentOrchestrator()
    orch.run_forever()