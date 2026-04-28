#!/usr/bin/env python3
import subprocess
import json

# Build the arguments for the mem0 tool
tool_args = {
    "user_id": "6061428"
}

# Build the tools list for multi-execute
tools_list = [
    {
        "tool_slug": "MEM0_GET_USER_MEMORY_STATS",
        "arguments": tool_args
    }
]

# Build the command for mcporter
cmd = [
    "mcporter", "call", "composio.COMPOSIO_MULTI_EXECUTE_TOOL",
    f"tools={json.dumps(tools_list)}",
    "sync_response_to_workbench=false",
    "session_id=your"
]

result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("Return code:", result.returncode)