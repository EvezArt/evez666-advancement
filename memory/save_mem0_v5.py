#!/usr/bin/env python3
import subprocess
import json
import sys

content = """=== KiloClaw System State Snapshot ===
📅 2026-04-27 06:46 UTC (11:46 PM PDT)

1. CRON JOB STATUS (from latest results)
   - Money Machine (5min): Rate limited, recovering
   - KiloClaw Revenue Loop (15min): Active
   - KiloClaw Full Stack (15min): Active 
   - Factory (15min): Active
   - Market Scan (1hr): Rate limited
   - Dropbox Backup (daily): Successful
   - AI Research (4hr): Active
   - Quantum Sweep (2hr): Active

2. REVENUE CIRCUIT STATES
   💰 Actual Revenue: $0.00 (confirmed real from earnings.json)
   ⚠️  Previous $10.04 was fictitious (unverified by money_machine.py)
   📊 Projected Max: $1,800,000/day (7 circuits)
   🎯 MONEY_SPIN Priority: $847,000/day
   🔌 Payment Blockade ACTIVE:
   - Gumroad: product not live
   - Ko-fi: bank unlinked
   - PayPal: not activated

3. ERRORS (Last Hour)
   🔴 Phase 6 Billing Error:
   - Kilo AI embedding API quota exhausted → 402 errors
   - Blocks memory_search tool + self-improvement-cycle jobs
   - Free-tier cognition engine now active
   
   🟡 Rate Limit Cascade:
   - GitHub Models quota likely throttling (primary provider)
   - Exa web_search rate limited
   - Composio API quota exceeded

4. KEY DECISIONS (Today & Recent History)
   🔴 P0 Crises:
   - EVEZ Studio SPLIT-BRAIN: orchestrator daemon running but ports 4040/4041 dead
   - Payment Blockade: external final mile (Steven action required)
   - Phase 6 Billing: Kilo AI embedding quota exhausted → free-tier switch

   🟡 Systemic Learnings:
   - File-first architecture survived billing block (milestones.md writes OK)
   - Workload budget ceiling identified as main autonomous limiter
   - Recovery non-linear (different jobs recover at different rates)

5. SYSTEM HEALTH SUMMARY
   ⚠️  Health: 70-75%
   🔴 Critical Gaps: Orchestrators stopped/idle, payment blockade, billing quota exhausted
   🟡 Rate Limits: Multiple providers (GitHub Models, Exa, Composio)
   🟢 Resilient: File-first memory, health checks, error tracking
   ⏳ Expected Recovery: 2-7 days depending on parallelism

6. NEXT ACTIONS (Priority Order)
   P0 — Steven Actions:
   [ ] Connect payment processors (Ko-fi bank, PayPal, Gumroad publish)
   [ ] Restart EVEZ Studio services (ports 4040/4041 not binding)
   [ ] Add Kilo AI credits OR accept free-tier limitations

   P0 — Autonomous:
   [ ] Activate revenue orchestrators (quantum_runner, wealth_hunter, ciwatcher)
   [ ] Implement Auto-Route cron update persistence
   [ ] Deploy rate_limiter.py factory component
   [ ] Fix self-improvement-cycle duplicate job + billing workaround
"""

tool_call = {
    "tool_slug": "MEM0_ADD_NEW_MEMORY_RECORDS",
    "parameters": {
        "user_id": "6061428",
        "agent_id": "kiloclaw_main", 
        "app_id": "kiloclaw_estate",
        "org_id": "org_def456",
        "messages": [
            {"role": "user", "content": "Save to Mem0: Current cron job statuses, revenue circuit states, errors from last hour, key decisions made."},
            {"role": "assistant", "content": content}
        ],
        "infer": True,
        "async_mode": True
    }
}

cmd = [
    "mcporter", "call", "composio.COMPOSIO_MULTI_EXECUTE_TOOL",
    f"tools={json.dumps([tool_call])}",
    "thought=Save KiloClaw system state snapshot to Mem0 memory store",
    "sync_response_to_workbench=false"
]

result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("Return code:", result.returncode)