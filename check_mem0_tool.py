import json

# Load payload
with open('/tmp/mem0_composio_payload.json') as f:
    payload = json.load(f)

# Try different tool slug permutations
tool_slugs = [
    "MEM0_ADD_NEW_MEMORY_RECORDS",
    "mem0_add_new_memory_records",
    "MEM0_MEMORY_ADD",
    "mem0_memory_add_records",
    "MEM0_ADD_MEMORY",
    "MEM0_CREATE_MEMORY_RECORDS"
]

print("Would try tool slugs:", tool_slugs)
print("\nPayload records:", len(payload['tools'][0]['arguments']['records']))
print("\nFirst record preview:")
first = payload['tools'][0]['arguments']['records'][0]['content']
print(first[:200] + "...")
