#!/bin/bash
# Save each memory record to Mem0 individually
cd /root/.openclaw/workspace

python3 -c "
import json, subprocess, sys

with open('.mem0_records.json') as f:
    records = json.load(f)

for i, rec in enumerate(records):
    args = json.dumps({
        'tools': [{
            'tool_slug': 'MEM0_ADD_NEW_MEMORY_RECORDS',
            'arguments': rec
        }],
        'thought': f'Mem0 batch {i+1}/4',
        'session_id': 'jack',
        'sync_response_to_workbench': False,
        'current_step': f'batch_{i+1}'
    })
    result = subprocess.run(
        ['mcporter', 'call', 'composio', '--tool', 'COMPOSIO_MULTI_EXECUTE_TOOL', '--args', args],
        capture_output=True, text=True
    )
    resp = json.loads(result.stdout) if result.returncode == 0 else {'error': result.stderr}
    print(f'Record {i+1}: success={resp.get(\"successful\", False)}')
    if not resp.get('successful'):
        print(f'  ERROR: {resp.get(\"error\") or resp}')
    else:
        results = resp.get('data', {}).get('results', [{}])
        if results:
            r = results[0].get('response', {})
            print(f'  Response: successful={r.get(\"successful\")}, error={r.get(\"error\")}')
"
