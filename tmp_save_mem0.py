#!/usr/bin/env python3
"""Save Shared Brain Consolidation #4 to Mem0 via Composio MCP"""
import subprocess
import json

mem0_record = {
    "user_id": "6061428",
    "agent_id": "main",
    "memories": [
        {
            "title": "Shared Brain Consolidation #4 — Resolution Stabilization (2026-04-24 15:08 UTC)",
            "content": """KiloClaw consolidation snapshot #4. Cron health: 81% (13/16 OK). EVEZ Platform verified healthy on port 8080 (not 4040/4041). Self-improvement cycle recovered on free tier (billing bypass validated). Factory v3 checkpoint stalled at cycle 40 despite builds through Apr 24 — build-to-deploy gap confirmed. Mem0 integration validated (06:22 UTC autosave via Composio MCP). Payment blockade active (Ko-fi/PayPal/Gumroad disconnected). Health stabilized at 76–81% for 9+ hours; non-monotonic recovery pattern validated. New patterns: (1) Port config drift (8080 vs docs 4040/4041), (2) Factory checkpoint desync (cycle_log vs checkpoint), (3) File-first memory resilience proven through full crisis, (4) Mem0 independent channel separate from Kilo AI billing, (5) Split-brain resolved via detection+human restart, (6) Revenue truth upheld ($0 actual, payment missing). Error axes: Phase 3 receding (~4 rate-limited, expected clearance ~16:00 UTC), Phase 6 billing resolved (free-tier active), split-brain resolved, payment blockade active. Actions pending: USER connect payment processors; SYSTEMIC: Factory checkpoint fix, Auto-Route cron automation, per-job quota budgeting.""",
            "metadata": {
                "category": "shared_brain_consolidation",
                "consolidation_sequence": 4,
                "cron_health_percent": 81,
                "ev_ez_port": 8080,
                "billing_status": "free_tier_active",
                "factory_status": "checkpoint_stalled_cycle40",
                "payment_blockade": True,
                "stabilization_hours": 9,
                "mem0_integration": "validated_independent",
                "trigger": "cron_98d02f1f"
            },
            "version": "v4",
            "unique_identifier": "consolidation_20260424_1508_kiloclaw_resolution_stabilization"
        }
    ]
}

args = json.dumps({
    "tools": [
        {
            "tool_slug": "MEM0_ADD_NEW_MEMORY_RECORDS",
            "arguments": mem0_record
        }
    ]
})

result = subprocess.run(
    ["mcporter", "call", "composio.COMPOSIO_MULTI_EXECUTE_TOOL", "--args", args],
    capture_output=True, text=True, timeout=30
)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("Return code:", result.returncode)
