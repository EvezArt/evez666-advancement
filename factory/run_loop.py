#!/usr/bin/env python3
import subprocess
import sys
import time

script = "/root/.openclaw/workspace/factory/continuous_factory_v3.py"
for i in range(10):
    print(f"Running cycle {i+1}/10")
    result = subprocess.run([sys.executable, script], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    time.sleep(2)