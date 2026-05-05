#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, timezone
import os

def run_mcporter(args):
    """Run mcporter command and return parsed JSON output."""
    cmd = ["mcporter"] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            print(f"mcporter failed: {result.stderr}", file=sys.stderr)
            return None
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"Failed to parse JSON output: {result.stdout}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error running mcporter: {e}", file=sys.stderr)
        return None

def get_cron_status():
    """Get cron job statuses from cron.json."""
    cron_path = '/root/.openclaw/workspace/cron.json'
    try:
        with open(cron_path, 'r') as f:
            data = json.load(f)
    except Exception as e:
        return f"Error reading cron.json: {e}"
    
    lines = []
    for job in data.get('jobs', []):
        name = job.get('name', 'Unknown')
        state = job.get('state', {})
        last_run_status = state.get('lastRunStatus', 'unknown')
        last_run_at_ms = state.get('lastRunAtMs', 'unknown')
        lines.append(f"- {name}: {last_run_status} (lastRunAtMs: {last_run_at_ms})")
    return "\n".join(lines)

def get_revenue_states():
    """Get revenue circuit states from money/ directory."""
    money_dir = '/root/.openclaw/workspace/money'
    info = []
    # earnings.json
    try:
        with open(f'{money_dir}/earnings.json', 'r') as f:
            earnings = json.load(f)
        info.append(f"Earnings: {json.dumps(earnings, indent=2)}")
    except Exception as e:
        info.append(f"Error reading earnings.json: {e}")
    
    # actual_revenue.json
    try:
        with open(f'{money_dir}/actual_revenue.json', 'r') as f:
            actual = json.load(f)
        info.append(f"Actual Revenue: {json.dumps(actual, indent=2)}")
    except Exception as e:
        info.append(f"Error reading actual_revenue.json: {e}")
    
    # revenue_tracker_latest.txt
    try:
        with open(f'{money_dir}/revenue_tracker_latest.txt', 'r') as f:
            latest = f.read().strip()
        info.append(f"Revenue Tracker Latest: {latest}")
    except Exception as e:
        info.append(f"Error reading revenue_tracker_latest.txt: {e}")
    
    # Check for any .json files in money/ that might contain circuit states
    import glob
    for f in glob.glob(f'{money_dir}/*.json'):
        if f.endswith('earnings.json') or f.endswith('actual_revenue.json'):
            continue
        try:
            with open(f, 'r') as fp:
                data = json.load(fp)
            info.append(f"{os.path.basename(f)}: {json.dumps(data, indent=2)}")
        except Exception:
            pass  # Not JSON or error, skip
    
    return "\n\n".join(info)

def get_recent_errors():
    """Get errors from the last hour from internal_executions.log."""
    log_path = '/root/.openclaw/workspace/internal_executions.log'
    try:
        with open(log_path, 'r') as f:
            lines = f.readlines()
    except Exception as e:
        return f"Error reading log: {e}"
    
    # We'll filter lines from the last hour (approximate)
    # Since the log format is: "2026-04-29 15:24:44 UTC: ..."
    # We'll parse the timestamp and compare to now - 1 hour.
    now = datetime.now(timezone.utc)
    one_hour_ago = now.timestamp() - 3600
    
    error_lines = []
    for line in lines:
        if ' UTC: ' not in line:
            continue
        timestamp_str = line.split(' UTC: ')[0]
        try:
            dt = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
            if dt.timestamp() >= one_hour_ago:
                # Check if it's an error line
                if 'Exec failed' in line or 'error' in line.lower() or 'rate_limit' in line.lower():
                    error_lines.append(line.strip())
        except ValueError:
            # If timestamp parsing fails, skip
            pass
    
    if not error_lines:
        return "No errors found in the last hour."
    return "\n".join(error_lines)

def get_key_decisions():
    """Get key decisions from milestones.md or mem0 payload files."""
    # Try to read milestones.md
    milestones_path = '/root/.openclaw/workspace/memory/milestones.md'
    try:
        with open(milestones_path, 'r') as f:
            content = f.read()
        # Get the last 20 lines or so
        lines = content.split('\n')
        # Take last 20 non-empty lines
        non_empty = [l for l in lines if l.strip()]
        recent = non_empty[-20:] if len(non_empty) > 20 else non_empty
        return "Recent decisions from milestones.md:\n" + "\n".join(recent)
    except Exception as e:
        return f"Could not read milestones.md: {e}"

def main():
    # Gather data
    cron_status = get_cron_status()
    revenue_states = get_revenue_states()
    recent_errors = get_recent_errors()
    key_decisions = get_key_decisions()
    
    # Compose the message content
    content = f"""Mem0 Auto-Memory Save - {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}

=== CRON JOB STATUSES ===
{cron_status}

=== REVENUE CIRCUIT STATES ===
{revenue_states}

=== ERRORS FROM LAST HOUR ===
{recent_errors}

=== KEY DECISIONS MADE ===
{key_decisions}
"""
    
    # Prepare the arguments for the MEM0_ADD_NEW_MEMORY_RECORDS tool
    # We'll use the composio.mem0 toolkit via mcporter
    # We need to call: mcporter call composio.mem0.MEM0_ADD_NEW_MEMORY_RECORDS ...
    # But we saw that the tool is not found under composio.mem0. However, the tool schemas show it's under MEM0 toolkit.
    # Let's try to use the multi-execute tool to call the MEM0 tool.
    # Alternatively, we can try to call the tool directly as mem0.MEM0_ADD_NEW_MEMORY_RECORDS if we can get the server name.
    # From the earlier list, the server is named "composio" and the toolkit is "mem0", but the tool is under the mem0 toolkit.
    # We need to use the multi-execute tool to call a tool from a toolkit.
    
    # Let's try to use the multi-execute tool.
    # We'll structure the call as:
    #   mcporter call composio.COMPOSIO_MULTI_EXECUTE_TOOL --args '{"tools":[{"tool_slug":"MEM0_ADD_NEW_MEMORY_RECORDS","arguments":{...}}],"sync_response_to_workbench":false,"memory":{},"session_id":"hunt"}'
    
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
                            "content": content
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
    
    # Write the args to a temporary file
    with open('/tmp/multi_exec_args.json', 'w') as f:
        json.dump(multi_exec_args, f, indent=2)
    
    # Call mcporter
    cmd = [
        "mcporter",
        "call",
        "composio.COMPOSIO_MULTI_EXECUTE_TOOL",
        "--args",
        "/tmp/multi_exec_args.json"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        print("mcporter stdout:", result.stdout)
        print("mcporter stderr:", result.stderr)
        print("Return code:", result.returncode)
        if result.returncode == 0:
            # Try to parse the output as JSON
            try:
                output = json.loads(result.stdout)
                print("Successfully saved to Mem0:", output)
            except json.JSONDecodeError:
                print("Saved to Mem0 (non-JSON output):", result.stdout)
        else:
            print("Failed to save to Mem0.")
    except Exception as e:
        print(f"Error executing mcporter: {e}")

if __name__ == '__main__':
    main()