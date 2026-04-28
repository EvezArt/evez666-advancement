#!/usr/bin/env python3
import subprocess
import json

messages = [
    {
        "role": "assistant",
        "content": "Backup cron job completed at 2026-04-26 20:37:49 UTC. Daily Dropbox Backup (cron 0 2 * * * exact) finished successfully. This is part of the regular backup schedule that runs daily at 2 AM exact time."
    }
]

args = [
    "mcporter", "call", "composio.COMPOSIO_MULTI_EXECUTE_TOOL",
    "session_id=look",
    "--args", json.dumps({
        "tools": [{
            "tool_slug": "MEM0_ADD_NEW_MEMORY_RECORDS",
            "arguments": {
                "agent_id": "421714",
                "messages": messages
            }
        }],
        "sync_response_to_workbench": False,
        "current_step": "ADD_BACKUP_MEMORY"
    })
]

result = subprocess.run(args, capture_output=True, text=True, timeout=30)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("Return code:", result.returncode)