#!/usr/bin/env python3

import subprocess
import json
import sys

# Content to save to Mem0
content = """Mem0 Auto-Memory cron job execution at 2026-04-29T06:18:00Z:

1. Current cron job statuses: 17 total jobs, all enabled. Key statuses: Money Machine (last ran ~50s ago, ok), KiloClaw Full Stack (last ran ~2m ago, ok), Market Scan (has 1 consecutive error - timeout), Auto-Route Failover (last ran ~2h ago, ok), Shared Brain Consolidation (last ran ~2h ago, ok), Quantum Sweep (last ran ~30m ago, ok), Revenue Tracker (last ran ~5m ago, ok), Factory (last ran ~50s ago, ok), KiloClaw Revenue Loop (last ran ~10h ago, ok), AI Research Lab (last ran ~12h ago, ok), Daily Dropbox Backup (last ran ~12h ago, ok), Cognition Enhancement Engine (next run in ~5 days), Memory Dreaming Promotion (daily at 3am).

2. Revenue circuit states: earnings.json shows total: $0, sources: [], last_updated: 2026-04-28T07:12:19Z, note: 'No real revenue. Previous $10.04 was fictitious (invented by money_machine.py without payment verification).'

3. Errors from last hour: Market Scan job (id: ad7578e7-2e99-4ad0-a10b-fe81d3d613f0) has 1 consecutive error with lastError: 'cron: job execution timed out'. No other errors detected in cron states.

4. Key decisions made: System continues autonomous operation with focus on revenue generation through money_machine.py, kiloclaw_loop.py, and inference_fabric.py. Auto-route failover mechanism active to adjust failing job schedules. Memory consolidation via Shared Brain and Mem0 integration ongoing. Quantum algorithm sweeps running every 3 hours."""

# Prepare the MCP tool call for COMPOSIO_MULTI_EXECUTE_TOOL
tool_input = {
    "tools": [
        {
            "tool_slug": "MEM0_ADD_NEW_MEMORY_RECORDS",
            "arguments": {
                "agent_id": "agent:main:cron:9132e9c2-a6be-4e7b-994c-ef5c26c552ef",
                "messages": [
                    {
                        "role": "assistant",
                        "content": content
                    }
                ]
            }
        }
    ],
    "sync_response_to_workbench": False,
    "session_id": "fear"  # from the search result
}

cmd = [
    "mcporter", "call", "composio.COMPOSIO_MULTI_EXECUTE_TOOL",
    "--args", json.dumps(tool_input)
]

print("Executing:", " ".join(cmd))
result = subprocess.run(cmd, capture_output=True, text=True)

print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("Return code:", result.returncode)

if result.returncode == 0:
    print("Successfully saved to Mem0")
else:
    print("Failed to save to Mem0")
    sys.exit(1)