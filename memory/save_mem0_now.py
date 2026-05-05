#!/usr/bin/env python3
import subprocess
import json

content = """=== KiloClaw Mem0 Auto-Memory Save ===
📅 2026-05-02 00:33 UTC (2026-05-01 17:33 America/Los_Angeles)

1️⃣ CRON JOB STATUSES
- Total Jobs: ~17 configured
- Operational: 10/17 (59%)
- Rate-limited: 4 jobs (Money Machine, Revenue Loop, Cognition Engine, Quantum Sweep)
- Billing-blocked: 1 job (self-improvement-cycle - Phase 6 Kilo AI quota exhausted)
- Split-brain: 1 persistent (EVEZ Studio ports 4040/4041 dead >18h)
- Adjusted intervals: Quantum Sweep 2hr→4hr, Revenue Loop 22.5min→60min

2️⃣ REVENUE CIRCUIT STATES
- Total Actual Revenue: $0.45 (verified Gumroad sales)
- Sources: api_sale ($0.05 Apr 24), api_quantum_calc ($0.10 ×4 on May 1)
- Running Services: Paid API :8081, Landing :3000, Economic Graph :8000
- Dead Services: EVEZ Studio HTTP :4040/:4041 (split-brain)
- Endpoints Active: POST /api/charge, GET /product/:id, POST /webhook/gumroad

3️⃣ ERRORS (Last Hour)
- No new system errors in logs
- Persistent: EVEZ Studio split-brain, payment processors disconnected >18h, Kilo AI embedding quota exhausted (402)
- API 404s on missing routes (/health, /api/status) - non-critical
- API 400s on missing task parameter - expected behavior

4️⃣ KEY DECISIONS MADE
- Revenue Activation Rule EXECUTED: Deployed API + landing immediately → $0.45 verified revenue
- Background Process Pattern: Use `nohup python3 file.py &` for persistent servers
- Phase 6 Billing: Switched to free-tier (kilocode/kilo-auto/free) to restore learning capability
- Auto-Route: Rate limits detected, intervals adjusted
- Self-improvement: File-first memory system proved resilient during billing failure"""

tool_call = {
    "tool_slug": "MEM0_ADD_NEW_MEMORY_RECORDS",
    "parameters": {
        "user_id": "6061428",
        "agent_id": "kiloclaw_main",
        "app_id": "kiloclaw_estate",
        "org_id": "org_def456",
        "run_id": "9132e9c2-a6be-4e7b-994c-ef5c26c552ef",
        "messages": [
            {"role": "user", "content": "Save to Mem0: 1) Current cron job statuses 2) Revenue circuit states from /root/.openclaw/workspace/money/ 3) Any errors from last hour 4) Key decisions made."},
            {"role": "assistant", "content": content}
        ],
        "infer": True,
        "async_mode": True
    }
}

cmd = [
    "mcporter", "call", "composio.COMPOSIO_MULTI_EXECUTE_TOOL",
    f'tools={json.dumps([tool_call])}',
    "thought=Save KiloClaw system state snapshot to Mem0 memory store",
    "sync_response_to_workbench=false"
]

result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
print("=== Mem0 Save Result ===")
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)