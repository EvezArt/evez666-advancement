import json
from composio_workbench_helpers import run_composio_tool

# Memory batch - 4 records
records = [
    {
        "user_id": "6061428",
        "agent_id": "main",
        "infer": False,
        "async_mode": False,
        "messages": [
            {"role": "user", "content": "Mem0 Auto-Memory Snapshot - 2026-04-24 10:16 UTC"},
            {"role": "assistant", "content": "CATEGORY 1: CRON JOB STATUSES (16 total). OK: 10 (Mem0 Auto-Memory, Revenue Tracker, Factory, Money Machine, Full Stack, Auto-Route Failover, Sphinx Letters, Shared Brain Consolidation, KiloClaw Revenue Loop, Quantum Sweep). Recovering: 4 (Money Machine rate_limited 2 consecutive, Revenue Tracker, Full Stack, Cognition Enhancement). ERROR: 2 (Self-Improvement Cycle 402 billing blocked 2 consecutive, Market Scan edit error). Persistent: Quantum Sweep. Churn 12%. Health 59%. Cognition Engine billing-blocked (402 Kilo AI quota exhausted)."}
        ]
    },
    {
        "user_id": "6061428",
        "agent_id": "main",
        "infer": False,
        "async_mode": False,
        "messages": [
            {"role": "user", "content": "Revenue Circuit States"},
            {"role": "assistant", "content": "CATEGORY 2: REVENUE CIRCUITS. Total earnings: $0.00 (real). Previous $10.04 fictitious (no payment processor). Products: quantum_calc $0.1, analysis $0.05, search $0.01, evez_template $29, prompt_pack $19. Projected $1.8M/day. Activation Rule TRIGGERED 2026-04-23T05:06:00Z. Status: circuits_activated_but_payment_blocked_and_money_machine_degraded. Payment Blockade >18h (gumroad blocked, ko-fi bank unlinked, paypal not activated). Money Machine: rate_limited 2 consecutive. Orchestrators ACTIVE (ci_watcher, wealth_hunter, quantum_runner)."}
        ]
    },
    {
        "user_id": "6061428",
        "agent_id": "main",
        "infer": False,
        "async_mode": False,
        "messages": [
            {"role": "user", "content": "Errors from Last Hour"},
            {"role": "assistant", "content": "CATEGORY 3: ERRORS LAST HOUR. quantum_runner: 'No module named qiskit' recurring every minute since 09:08 UTC (20+). Cognition Enhancement: 402 Kilo AI embedding quota exhausted (2 consecutive). Self-Improvement Cycle: 402 billing error (2 consecutive). Money Machine: rate_limit (2 consecutive). Market Scan: 'Edit: in memory/2026-04-24.md failed'. EV_EZ Studio: Port-binding failure PID 2932 but ports 4040/4041 dead (>11h split-brain). Active errors: 5. Phase 3 Systemic Cascade: receding. Phase 6 Billing Exhaustion: active."}
        ]
    },
    {
        "user_id": "6061428",
        "agent_id": "main",
        "infer": False,
        "async_mode": False,
        "messages": [
            {"role": "user", "content": "Key Decisions & Learnings"},
            {"role": "assistant", "content": "CATEGORY 4: KEY DECISIONS/LEARNINGS. 1) FILE-FIRST RESILIENCE CONFIRMED: heartbeat-state.json updates continue via file writes even when AI cognition 402-billed. Monitoring persistence independent of AI. 2) MONITORING INTELLIGENCE ≠ PERSISTENCE: Separated analysis from persistence, proven during Phase 6. 3) AUTO-ROUTE FAILOVER adjustments: Quantum Sweep 2hr→4hr, Auto-Route 45min→60min, Revenue Loop 22.5min→60min. Note: cron update automation gap - detection works but manual edit still needed. 4) PHASE TAXONOMY: Phase 3 receding, Phase 5 fixed, Phase 6 active. 5) CRISIS RECOVERY SEQUENCE validated: monitor→triad→config→EVEZ→payment. 6) REVENUE TRIAD health mixed: Full Stack OK, Revenue Tracker OK, Money Machine degraded. 7) SPLIT-BRAIN PERSISTENT: agent layer >11h but EVEZ Studio (4040/4041) and ROM-S (3847) endpoints offline. 8) PAYMENT BLOCKADE independent external layer. 9) FILE CONCURRENCY: 0% conflict recent. NEXT USER ACTIONS: Fix EVEZ Studio ports; Connect payment processors; Add Kilo AI credits or switch free tier; Install qiskit; Close cron update automation gap."}
        ]
    }
]

results = []
for i, record in enumerate(records):
    result, error = run_composio_tool("MEM0_ADD_NEW_MEMORY_RECORDS", record)
    if error:
        print(f"Record {i+1} ERROR:", error)
    else:
        print(f"Record {i+1} SUCCESS:", json.dumps(result, indent=2)[:300])
    results.append({"record": i+1, "result": result, "error": error})

print("\n=== SUMMARY ===")
for r in results:
    status = "OK" if not r["error"] else f"FAIL: {r['error']}"
    print(f"  Record {r['record']}: {status}")

# Return final summary
all_ok = all(not r["error"] for r in results)
print("\nAll records saved successfully:" if all_ok else "\nSome records failed to save")
