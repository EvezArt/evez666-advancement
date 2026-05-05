#!/usr/bin/env python3

import subprocess
import json
import sys

event_id = "592b4a98-a510-4477-a260-57ed2bff286b"

# Prepare the MCP tool call for COMPOSIO_MULTI_EXECUTE_TOOL to get event status
tool_input = {
    "tools": [
        {
            "tool_slug": "MEM0_GET_EVENT_STATUS_BY_EVENT_ID",
            "arguments": {
                "event_id": event_id
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
    print("Successfully checked Mem0 event status")
else:
    print("Failed to check Mem0 event status")
    sys.exit(1)