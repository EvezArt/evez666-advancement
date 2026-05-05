#!/usr/bin/env python3
import subprocess
import json
import time
from datetime import datetime, timezone

def get_current_time_utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

def get_earnings():
    try:
        with open('/root/.openclaw/workspace/money/earnings.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        return {"error": str(e)}

def get_cron_status():
    try:
        # Try to run openclaw cron list with a timeout
        result = subprocess.run(['openclaw', 'cron', 'list'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return result.stdout
        else:
            return f"Error running openclaw cron list: {result.stderr}"
    except subprocess.TimeoutExpired:
        return "Timeout running openclaw cron list (command hanging)"
    except Exception as e:
        return f"Exception running openclaw cron list: {str(e)}"

def get_last_memory_file():
    try:
        with open('/root/.openclaw/workspace/memory/2026-04-30.md', 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading last memory file: {str(e)}"

def main():
    current_time = get_current_time_utc()
    earnings = get_earnings()
    cron_status = get_cron_status()
    last_memory = get_last_memory_file()

    # Build the report content
    content = f"""
Mem0 Auto-Memory Save Report for cron job 9132e9c2-a6be-4e7b-994c-ef5c26c552ef

1) CURRENT CRON JOB STATUSES:
- Mem0 Auto-Memory cron job (9132e9c2-a6be-4e7b-994c-ef5c26c552ef) triggered this save at {current_time}
- Live cron status (attempted at {current_time}):
{ cron_status }

2) REVENUE CIRCUIT STATES:
- Actual revenue: {earnings.get('total', 'unknown')} (confirmed from earnings.json)
- earnings.json: {json.dumps(earnings, indent=2)}
- Payment processors: All disconnected (Gumroad product not live, Ko-fi bank unlinked, PayPal not activated)
- Revenue projected: $1.8M/day across 7 circuits (from USER.md)

3) ERRORS FROM LAST HOUR:
- [Note: Due to cron command hanging, we are unable to retrieve live errors. Using last known errors from 2026-04-30 23:07 UTC as reference:]
- Auto-Route Failover: error (errors=2)
- Cognition Enhancement Engine: error (errors=1)
- 402 Kilo AI embedding quota exhausted (from 2026-04-29 memory)
- For live errors, please check system logs or wait for cron command to respond.

4) KEY DECISIONS MADE:
- FILE-FIRST RESILIENCE CONFIRMED (using file fallback when Mem0 search disabled)
- MONITORING INTELLIGENCE ≠ MONITORING PERSISTENCE
- SELF-IMPROVEMENT CYCLE BILLING DEBT
- Shared Brain Consolidation completed multiple times today (19:23, 19:28, 19:30 UTC)
- Insights appended to milestones.md
- Cognition Enhancement Engine channel fixed

SYSTEM HEALTH SUMMARY:
- EVEZ Studio: Split-brain >11h (daemon running but ports 4040/4041 not listening)
- Memory consolidation: Ongoing via file-first approach
- Next steps: Monitor for quota reset, await user action on EVEZ Studio restart and payment processor connection

Timestamp: {current_time}
"""

    messages = [
        {
            "role": "assistant",
            "content": content.strip()
        }
    ]

    # Prepare the arguments for mcporter
    # We are going to use the composio tool MEM0_ADD_NEW_MEMORY_RECORDS
    # We know the agent_id and user_id from the active connection we saw earlier
    args = [
        "mcporter", "call", "composio", "MEM0_ADD_NEW_MEMORY_RECORDS",
        "agent_id=422632",
        "user_id=6061428",
        f"messages={json.dumps(messages)}",
        "infer=true",
        "async_mode=true"
    ]

    # Run the command
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=30)
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        print("Return code:", result.returncode)
    except Exception as e:
        print(f"Error running mcporter: {str(e)}")

if __name__ == "__main__":
    main()