#!/usr/bin/env python3
"""Enumerate all available OpenClaw surfaces, plugins, services."""
import subprocess, json, os, sys

print("=" * 60)
print("OPENCLAW SURFACE AUDIT")
print("=" * 60)

# 1. Core runtime info
print("\n[1] Runtime Context:")
print(f"   Host: {subprocess.check_output(['hostname']).decode().strip()}")
print(f"   Node: {subprocess.check_output(['node', '--version']).decode().strip()}")
print(f"   Workspace: {os.getcwd()}")

# 2. Gateway status
print("\n[2] Gateway Status:")
try:
    result = subprocess.run(['openclaw', 'gateway', 'status'], capture_output=True, text=True, timeout=10)
    print(result.stdout[:2000])
except Exception as e:
    print(f"   Error: {e}")

# 3. Installed plugins/skills
print("\n[3] Installed Skills/Plugins:")
skills_dir = '/root/.openclaw/workspace/skills'
if os.path.exists(skills_dir):
    skills = [s for s in os.listdir(skills_dir) if os.path.isdir(os.path.join(skills_dir, s))]
    print(f"   Total: {len(skills)}")
    for s in sorted(skills):
        print(f"   - {s}")
else:
    print("   No skills directory")

# 4. Available MCP servers (mcporter)
print("\n[4] MCP Servers (mcporter):")
try:
    result = subprocess.run(['mcporter', 'list'], capture_output=True, text=True, timeout=10)
    print(result.stdout[:2000] or result.stderr[:2000])
except Exception as e:
    print(f"   mcporter not available: {e}")

# 5. External services credentials
print("\n[5] External Services (credentials):")
creds_dir = '/root/.openclaw/workspace/credentials'
if os.path.exists(creds_dir):
    print(f"   Found: {creds_dir}")
    for root, dirs, files in os.walk(creds_dir):
        for f in files:
            path = os.path.join(root, f)
            size = os.path.getsize(path)
            print(f"   - {f} ({size} bytes)")
else:
    print("   No credentials directory")

# 6. Open ports/services
print("\n[6] Network Services:")
try:
    result = subprocess.run(['ss', '-tlnp'], capture_output=True, text=True, timeout=10)
    lines = result.stdout.strip().split('\n')
    for line in lines[:20]:
        print(f"   {line}")
except Exception as e:
    print(f"   Error: {e}")

# 7. Browser profiles
print("\n[7] Browser Profiles:")
try:
    result = subprocess.run(['browser', 'profiles'], capture_output=True, text=True, timeout=10)
    print(result.stdout[:1000] or result.stderr[:1000])
except Exception as e:
    print(f"   browser tool not available: {e}")

# 8. Cron jobs
print("\n[8] Cron Jobs:")
try:
    result = subprocess.run(['openclaw', 'cron', 'list'], capture_output=True, text=True, timeout=10)
    print(result.stdout[:2000])
except Exception as e:
    print(f"   Error: {e}")

# 9. Memory files
print("\n[9] Memory Context:")
mem_dir = '/root/.openclaw/workspace/memory'
if os.path.exists(mem_dir):
    files = sorted(os.listdir(mem_dir))
    print(f"   Files: {len(files)}")
    for f in files[-10:]:
        path = os.path.join(mem_dir, f)
        size = os.path.getsize(path)
        print(f"   - {f} ({size} bytes)")

# 10. Active sessions
print("\n[10] Active Sessions:")
try:
    result = subprocess.run(['openclaw', 'sessions', 'list'], capture_output=True, text=True, timeout=10)
    print(result.stdout[:2000])
except Exception as e:
    print(f"   Error: {e}")

# 11. Ontology entities
print("\n[11] Ontology Graph:")
graph_path = '/root/.openclaw/workspace/memory/ontology/graph.jsonl'
if os.path.exists(graph_path):
    with open(graph_path) as f:
        lines = f.readlines()
    print(f"   Entities/relations: {len(lines)}")
    counts = {}
    for line in lines:
        try:
            obj = json.loads(line)
            t = obj.get('entity', {}).get('type', 'relation')
            counts[t] = counts.get(t, 0) + 1
        except:
            pass
    for k, v in sorted(counts.items()):
        print(f"   - {k}: {v}")
else:
    print("   No ontology graph")

print("\n" + "=" * 60)
print("AUDIT COMPLETE")
print("=" * 60)
