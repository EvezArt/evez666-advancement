#!/usr/bin/env python3
import subprocess
import json

# Test with a simple read operation first
tool_args = {
    "user_id": "6061428"
}

tools_list = [
    {
        "tool_slug": "MEM0_GET_USER_MEMORY_STATS",
        "arguments": tool_args
    }
]

cmd = [
    "mcporter", "call", "composio.COMPOSIO_MULTI_EXECUTE_TOOL",
    f"tools={json.dumps(tools_list)}",
    "sync_response_to_workbench=false",
    "session_id=your"  # Using session_id from earlier search
]

print("Running command:", " ".join(cmd))
result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("Return code:", result.returncode)