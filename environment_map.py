#!/usr/bin/env python3
import os, json, subprocess, sys
from datetime import datetime

def sh(cmd):
    try:
        result = subprocess.run(cmd, shell=False, capture_output=True, text=True, timeout=5)
        return result.stdout.strip(), result.returncode
    except Exception as e:
        return str(e), 1

print("=" * 70)
print("ENVIRONMENT MAP — KILOCLAW SELF-REFERENTIAL SURVEY")
print("=" * 70)

print("\n[IDENTITY]")
print(f"  Assistant : KiloClaw")
print(f"  Runtime   : OpenClaw agent=main")
print(f"  Host      : {sh(['hostname'])[0]}")
print(f"  Workspace : {os.getcwd()}")
print(f"  Timestamp : {datetime.now().isoformat()}")

print("\n[SELF — This Agent]")
print(f"  PID       : {os.getpid()}")
print(f"  Python    : {sys.version.split()[0]}")

ws = '/root/.openclaw/workspace'
print("\n[WORKSPACE FOOTPRINT]")
total = 0
for root, dirs, files in os.walk(ws):
    for f in files:
        try:
            total += os.path.getsize(os.path.join(root, f))
        except: pass
print(f"  Total size : ~{total/1024/1024:.1f} MB")

entries = sorted(os.listdir(ws))
print(f"  Top-level ({len(entries)}): {', '.join(entries[:12])}")

print("\n[MEMORY CONTEXT]")
mem_dir = os.path.join(ws, 'memory')
if os.path.exists(mem_dir):
    mem_files = sorted(os.listdir(mem_dir))
    print(f"  Files: {len(mem_files)}")
    for f in mem_files[-6:]:
        sz = os.path.getsize(os.path.join(mem_dir, f))
        print(f"    {f}  ({sz} B)")
    graph = os.path.join(mem_dir, 'ontology', 'graph.jsonl')
    if os.path.exists(graph):
        with open(graph) as fh:
            lines = fh.readlines()
        print(f"  Ontology: {len(lines)} entries")
else:
    print("  No memory directory")

print("\n[CRON JOBS]")
out, code = sh(['openclaw', 'cron', 'list'])
if code == 0:
    jobs = [l for l in out.split('\n') if l.strip()]
    print(f"  Jobs: {len(jobs)}")
    for j in jobs[:6]:
        print(f"    {j}")
else:
    print(f"  Error: {out}")

print("\n[SKILLS]")
skills_dir = os.path.join(ws, 'skills')
if os.path.exists(skills_dir):
    skills = sorted([s for s in os.listdir(skills_dir) if os.path.isdir(os.path.join(skills_dir, s))])
    print(f"  Count: {len(skills)} — {', '.join(skills[:8])}")

print("\n[MCP SERVERS]")
out, code = sh(['mcporter', 'list'])
if code == 0:
    print(out[:400])
else:
    print("  mcporter unavailable")

print("\n[CREDENTIAL STORES]")
creds = os.path.join(ws, 'credentials')
if os.path.exists(creds):
    for root, dirs, files in os.walk(creds):
        for f in files:
            sz = os.path.getsize(os.path.join(root, f))
            print(f"    {f}  ({sz} B)")
else:
    print("  None")

print("\n[VIDEO ASSETS]")
for f in os.listdir(ws):
    if f.endswith('.mp4'):
        sz = os.path.getsize(os.path.join(ws, f))
        print(f"    {f}  ({sz} B)")

# ── Self-map record ─────────────────────────────────────────────────────────
print("\n[METACOGNITION — Self-Map Log]")
record = {
    "mapping_run": datetime.now().isoformat(),
    "workspace": ws,
    "top_level_entries": entries,
    "memory_files": mem_files if 'mem_files' in locals() else [],
    "ontology_entities": len(lines) if 'lines' in locals() else 0,
    "skills_count": len(skills) if 'skills' in locals() else 0,
    "cron_job_count": len(jobs) if 'jobs' in locals() else 0,
    "mapped_by": "KiloClaw-self-scan",
    "persisted_to": os.path.join(mem_dir, 'self_maps')
}
log_dir = os.path.join(mem_dir, 'self_maps')
os.makedirs(log_dir, exist_ok=True)
log_path = os.path.join(log_dir, f"env_map_{datetime.now():%Y%m%d_%H%M%S}.json")
with open(log_path, 'w') as fh:
    json.dump(record, fh, indent=2)
print(f"  Saved: {log_path}")

print("\n" + "=" * 70)
print("MAP COMPLETE — Environment captured in memory/self_maps/")
print("=" * 70)
