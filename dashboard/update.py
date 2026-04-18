#!/usr/bin/env python3
"""
EVEZ LIVE DASHBOARD - Generates real-time stats
"""

import json
import os
from datetime import datetime

OUTPUT = "/root/.openclaw/workspace/dashboard/data.json"

def get_stats():
    stats = {
        "timestamp": datetime.now().isoformat(),
        "agents": {
            "omni_agent": check_process("omni_agent"),
            "quantum_runner": check_process("quantum_runner"),
            "wealth_hunter": check_process("wealth_hunter"),
            "ci_watcher": check_process("ci_watcher"),
        },
        "quantum": {
            "runs": count_lines("/root/.openclaw/workspace/agents/quantum_runner.log"),
            "last_state": get_last_quantum(),
        },
        "cycles": count_lines("/root/.openclaw/workspace/agents/omni_agent.log", "CYCLE"),
        "github": {
            "changes": count_git_changes(),
        },
        "cheatcodes": find_cheatcodes(),
    }
    return stats

def check_process(name):
    import subprocess
    result = subprocess.run(["pgrep", "-f", name], capture_output=True)
    return "running" if result.returncode == 0 else "stopped"

def count_lines(filepath, pattern=None):
    if not os.path.exists(filepath):
        return 0
    with open(filepath) as f:
        lines = f.readlines()
    if pattern:
        return sum(1 for l in lines if pattern in l)
    return len(lines)

def get_last_quantum():
    filepath = "/root/.openclaw/workspace/agents/quantum_runner.log"
    if not os.path.exists(filepath):
        return "none"
    with open(filepath) as f:
        for line in reversed(f.readlines()):
            if "EXECUTED" in line:
                return line.strip()
    return "none"

def count_git_changes():
    import subprocess
    result = subprocess.run(["git", "-C", "/root/.openclaw/workspace", "status", "--porcelain"], 
                           capture_output=True, text=True)
    return len([l for l in result.stdout.strip().split("\n") if l])

def find_cheatcodes():
    import subprocess
    result = subprocess.run(
        ["find", "/root/.openclaw/workspace", "-name", "*.md", "-type", "f"],
        capture_output=True, text=True
    )
    files = [f for f in result.stdout.strip().split("\n") if f]
    cheats = []
    keywords = ["cheat", "note", "todo", "reminder", "setup", "quickstart", "password", "key", "token"]
    for f in files[:20]:
        try:
            with open(f) as file:
                if any(k in file.read().lower() for k in keywords):
                    cheats.append(f.replace("/root/.openclaw/workspace", ""))
        except:
            pass
    return cheats[:10]

if __name__ == "__main__":
    stats = get_stats()
    with open(OUTPUT, "w") as f:
        json.dump(stats, f, indent=2)
    print(f"Updated: {OUTPUT}")
    print(f"Agents: {sum(1 for v in stats['agents'].values() if v == 'running')}/4")
    print(f"Quantum: {stats['quantum']['runs']} runs")
    print(f"Cheatcodes: {len(stats['cheatcodes'])} found")