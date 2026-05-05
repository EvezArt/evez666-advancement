import json
import subprocess

# Build the arguments for the multi-execute tool
multi_exec_args = {
    "tools": [
        {
            "tool_slug": "MEM0_ADD_NEW_MEMORY_RECORDS",
            "arguments": {
                "agent_id": "agent:main:cron:9132e9c2-a6be-4e7b-994c-ef5c26c552ef",
                "messages": [
                    {
                        "role": "system",
                        "content": "test"
                    }
                ],
                "infer": True
            }
        }
    ],
    "sync_response_to_workbench": False,
    "memory": {},
    "session_id": "hunt"
}

# Write to a temporary file
with open('/tmp/test_args.json', 'w') as f:
    json.dump(multi_exec_args, f)

# Call mcporter
cmd = [
    "mcporter",
    "call",
    "composio.COMPOSIO_MULTI_EXECUTE_TOOL",
    "--args",
    "/tmp/test_args.json"
]

print("Running:", " ".join(cmd))
result = subprocess.run(cmd, capture_output=True, text=True)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("Return code:", result.returncode)