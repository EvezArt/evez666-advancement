#!/usr/bin/env python3
import subprocess
import json

content = """=== KiloClaw System State Snapshot ===
📅 2026-04-24 11:16 UTC (4:16 AM PDT)

CRON STATUS: 16 jobs, 13 healthy (81%), 3 errors (billing 402, rate_limit), 2 recovering.
REVENUE: $0.00 actual, $1.8M/day projected, products ready but payment blockade active.
ERRORS: Phase 6 billing quota exhausted, rate_limit cascade improving (13/17 OK now vs 4/17 at worst).
DECISIONS: EVEZ split-brain P0, billing failover to free-tier, file-first resilience validated, Auto-Route gap elevated.
"""

tool_call = {
    "tool_slug": "MEM0_ADD_NEW_MEMORY_RECORDS",
    "parameters": {
        "user_id": "6061428",
        "agent_id": "kiloclaw_main",
        "app_id": "kiloclaw_estate",
        "messages": [
            {"role": "user", "content": "Save system state to Mem0"},
            {"role": "assistant", "content": content}
        ],
        "infer": True,
        "async_mode": True
    }
}

payload = {
    "tools": [tool_call],
    "thought": "Save KiloClaw auto-memory snapshot",
    "sync_response_to_workbench": False
}

# Print the exact JSON we'll send
print("Payload:", json.dumps(payload, indent=2)[:500])

cmd = [
    "mcporter", "call", "composio.COMPOSIO_MULTI_EXECUTE_TOOL",
    f"tools={json.dumps([tool_call])}",
    "thought=Save KiloClaw auto-memory snapshot",
    "sync_response_to_workbench=false"
]

print("\nCmd:", cmd)
result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
print("\nSTDOUT:", result.stdout[:2000])
print("STDERR:", result.stderr[:1000])
print("Return code:", result.returncode)
