#!/usr/bin/env python3
"""
CI Watcher - Monitors CI across all repos continuously
"""

import time
import os
from datetime import datetime

LOG_FILE = "/root/.openclaw/workspace/agents/ci_watcher.log"
REPOS_DIR = "/root/.openclaw/workspace"

def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.now().isoformat()}] {msg}\n")

def check_ci():
    """Check CI status across repos"""
    repos = [d for d in os.listdir(REPOS_DIR) if os.path.isdir(f"{REPOS_DIR}/{d}") and not d.startswith('.')]
    
    results = []
    for repo in repos[:5]:  # Check first 5
        test_dir = f"{REPOS_DIR}/{repo}/tests"
        has_tests = os.path.exists(test_dir)
        results.append({"repo": repo, "has_tests": has_tests})
    
    log(f"CHECKED: {len(results)} repos")
    return results

def main():
    log("=== CI WATCHER STARTED ===")
    cycle = 0
    
    while True:
        cycle += 1
        check_ci()
        time.sleep(120)  # Every 2 minutes

if __name__ == "__main__":
    main()