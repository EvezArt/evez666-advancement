#!/usr/bin/env python3
import subprocess
import json

payload = {
    "user_id": "6061428",
    "agent_id": "kiloclaw_main",
    "app_id": "kiloclaw_estate",
    "run_id": "auto-memory-20260423-2318",
    "messages": [
        {
            "role": "system",
            "content": "KiloClaw Systemic Statecapture — 2026-04-23 23:18 UTC"
        },
        {
            "role": "user",
            "content": """=== CRON JOB STATUS SUMMARY ===
Total jobs: 17
- OK: 13 (76%)
- Errors: 4 (24%)
Critical issues:
• Revenue Tracker: ERROR (rate_limit, 2 consecutive)
• Auto-Route Failover: ERROR (rate_limit, 2 consecutive)
• Self-improvement-cycle (main): ERROR (billing 402, 16 consecutive)
• Self-improvement-cycle (dup): ERROR (billing 402, 16 consecutive)

Recovering:
• Money Machine: rate_limited (2 consecutive)
• Market Scan: recovering
• Quantum Sweep: recovering

=== REVENUE CIRCUIT STATES ===
Actual Revenue: $10.04 total ($0.05 api_sale + $9.99 content_sale)
Projected: $1.8M/day (theoretical)
Status: circuits ACTIVE but payment DISCONNECTED
Money Machine: rate_limited (recovering)
Revenue Tracker: OK
Full Stack: OK
Orchestrators: ACTIVE
Payment Blockade: TRUE (Gumroad/Ko-fi/PayPal all blocked)

=== ERRORS LAST HOUR ===
1. rate_limit (GitHub Models) — affecting 4–6 jobs, 1–2 consecutive each
   - Expected resolution: 22:00 UTC quota reset
2. billing_402 (Kilo AI embeddings) — self-improvement-cycle (16 consecutive errors)
   - Severity: HIGH, memory_search tool disabled

System Health: 76% OK

=== KEY DECISIONS MADE ===
1. PHASE 6 BILLING ERROR — Kilo AI embedding API 402 quota exhausted
2. EVEZ STUDIO SPLIT-BRAIN — >11h, orchestrator PID 2932 but ports 4040/4041 dead
3. CONFIG DECAY FIXED — self-improvement-channel misconfig resolved at 18:18 UTC
4. MONITORING TIER RESTORED — Cognition Engine + Shared Brain recovered
5. REVENUE TRIAD MIXED — Full Stack & Revenue Tracker OK, Money Machine degraded
6. AUTO-ROUTE GAP ELEVATED — detection-only without cron update automation
7. FILE-FIRST MEMORY RESILIENT — validated through crisis
8. DEDUPLICATION GAP — duplicate self-improvement-cycle jobs identified
9. PAYMENT BLOCKADE INDEPENDENT — external final mile separate from technical cascade
10. RECOVERY SEQUENCE MAPPED — monitor→triad→config→EVEZ→payment

=== CRISIS PHASES ===
Phase 1-5: RESOLVED/FIXED
Phase 6: ACTIVE (billing 402)

=== P0 ACTIONS ===
Steven: 1) Resolve Kilo AI billing, 2) Restart EVEZ Studio, 3) Connect payments
Auto: 1) Money Machine recovery (22:00 UTC), 2) Implement cron automation,
     3) Deploy rate_limiter.py

Timeline: 2-4 days parallel, 5-7 days sequential."""
    }
],
    "metadata": {
        "saved_by": "cron_Mem0_Auto-Memory",
        "job_id": "9132e9c2-a6be-4e7b-994c-ef5c26c552ef",
        "timestamp": "2026-04-23T23:18:00Z",
        "categories": [
            "cron_job_statuses",
            "revenue_circuit_states",
            "errors_last_hour",
            "key_decisions",
            "phase_6_billing",
            "ev_ez_split_brain",
            "payment_blockade",
            "recovery_roadmap",
            "systemic_crisis_analysis"
        ]
    }
}

# Call mcporter with JSON payload
cmd = ["mcporter", "call", "composio.MEM0_ADD_NEW_MEMORY_RECORDS", "--args", json.dumps(payload)]
result = subprocess.run(cmd, capture_output=True, text=True)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("Return code:", result.returncode)
