#!/usr/bin/env python3
"""API Health Monitor"""
import subprocess, json, time
from datetime import datetime

SERVICES = {"linear": {"priority": 1}, "slack": {"priority": 2}}

def check(name):
    start = time.time()
    try:
        r = subprocess.run(["mcporter","call",f"{name}.list_issues"],capture_output=True,timeout=10)
        return {"name":name,"status":"ok" if r.returncode==0 else "fail","latency":time.time()-start}
    except Exception as e:
        return {"name":name,"status":"error","error":str(e)}

print(f"=== EVEZ Health Check {datetime.now().isoformat()} ===")
for s in SERVICES:
    r = check(s)
    print(f"{'OK' if r['status']=='ok' else 'FAIL'}: {s}")
