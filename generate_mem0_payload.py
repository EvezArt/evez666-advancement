#!/usr/bin/env python3
import json, sys

payload = {
    "tools": [
        {
            "tool_slug": "MEM0_ADD_NEW_MEMORY_RECORDS",
            "arguments": {
                "user_id": "6061428",
                "infer": False,
                "async_mode": True,
                "messages": [
                    {
                        "role": "user",
                        "content": "CRON_JOB_STATUSES - 2026-04-24 18:16Z - KiloClaw Mem0 Auto-Memory. Cron health: 13/16 OK, 3 degraded: Money Machine (rate-limited 2 consecutive), Auto-Route (rate-limited), Revenue Loop (rate-limited). Critical systems (ROM-S, EVEZ, Factory, Orchestrators) running. Monitor: GitHub Models quota clearance ~20:00 UTC."
                    },
                    {
                        "role": "assistant",
                        "content": "REVENUE_CIRCUITS - 2026-04-24 18:16Z - Actual: $0.00. Theoretical: $1.8M/day. State: active_but_payment_disconnected. Payment blockade: Ko-fi bank unlinked, PayPal inactive, Gumroad not live. Money Machine: rate_limited_recovering (2 consecutive). USER ACTION: connect payment processors."
                    }
                ]
            }
        },
        {
            "tool_slug": "MEM0_ADD_NEW_MEMORY_RECORDS",
            "arguments": {
                "user_id": "6061428",
                "infer": False,
                "async_mode": True,
                "messages": [
                    {
                        "role": "user",
                        "content": "ERRORS_LAST_HOUR - 2026-04-24 18:16Z - Active errors: 5. Breakdown: Phase 3 systemic cascade (4), Phase 6 billing (2: self-improvement-cycle 402, resolved via free-tier), other (3). Rate-limit: RECOVERING - 10/17 OK (59%). System health: stabilized 81% for 12+ hours. Churn normalized to ~2-3%/hr baseline. No new error axes in 12h - crisis cascade exhausted. Split-brain RESOLVED. Factory checkpoint desynchronization bug identified."
                    },
                    {
                        "role": "assistant",
                        "content": "KEY_DECISIONS - 2026-04-24 18:16Z - Decisions: 1) Free-tier billing bypass validated. 2) EVEZ split-brain recovery manual. 3) Mem0 integration independent from Kilo AI billing. 4) File-first memory resilience proven. 5) Phase 5 config decay FIXED. 6) Auto-Route speedrun adjustments applied. 7) Build-to-deploy gap root cause: checkpoint persistence bug in continuous_factory_v3.py. Pending: fix checkpoint OR manual deployment. Revenue activation rule TRIGGERED but payment blockade blocks execution."
                    }
                ]
            }
        }
    ],
    "memory": {
        "mem0_save": [
            "KiloClaw Mem0 Auto-Memory save at 2026-04-24T18:16Z via mcporter",
            "Batch 1+2: Combined CRON+REVENUE and ERRORS+DECISIONS records"
        ]
    },
    "sync_response_to_workbench": False,
    "current_step": "SAVING_ALL_RECORDS",
    "current_step_metric": "2/2 batches",
    "session_id": "hill"
}

print(json.dumps(payload, ensure_ascii=False, separators=(',', ':')))
