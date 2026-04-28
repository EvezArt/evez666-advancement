#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import time

# Path to the cron jobs file
JOBS_FILE = '/root/.openclaw/cron/jobs.json'
BACKUP_FILE = '/root/.openclaw/cron/jobs.json.backup.' + str(int(time.time()))

def run_command(cmd, timeout=30):
    """Run a command and return (success, output)."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except Exception as e:
        return False, str(e)

def load_jobs():
    """Load the jobs from the JSON file."""
    with open(JOBS_FILE, 'r') as f:
        data = json.load(f)
    return data

def save_jobs(data):
    """Save the jobs to the JSON file."""
    # Create a backup
    subprocess.run(f"cp {JOBS_FILE} {BACKUP_FILE}", shell=True, check=True)
    with open(JOBS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def ms_to_human(ms):
    """Convert milliseconds to a human-readable string for the --every flag."""
    total_seconds = ms / 1000
    days = int(total_seconds // (24 * 3600))
    hours = int((total_seconds % (24 * 3600)) // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0 and not parts:  # Only show seconds if no larger units
        parts.append(f"{seconds}s")
    
    # If we have no parts (i.e., 0 ms), return "0s"
    if not parts:
        return "0s"
    return "".join(parts)

def main():
    print("Starting auto-route failover...")
    
    # Load current jobs
    data = load_jobs()
    jobs = data.get('jobs', [])
    
    adjustments = []
    retries = []
    
    for job in jobs:
        job_id = job.get('id')
        name = job.get('name')
        state = job.get('state', {})
        schedule = job.get('schedule', {})
        consecutive_errors = state.get('consecutiveErrors', 0)
        last_run_status = state.get('lastRunStatus')
        
        # Check for consecutive errors > 3
        if consecutive_errors > 3 and schedule.get('kind') == 'every':
            every_ms = schedule.get('everyMs', 0)
            if every_ms > 0:
                new_every_ms = int(every_ms * 1.5)
                human_interval = ms_to_human(new_every_ms)
                
                # Attempt to update the job via openclaw cron edit
                cmd = f"openclaw cron edit {job_id} --every {human_interval}"
                success, output = run_command(cmd, timeout=30)
                
                if success:
                    adjustments.append(f"Job '{name}' (ID: {job_id}) interval increased from {every_ms}ms to {new_every_ms}ms ({human_interval})")
                    # Update the in-memory schedule for consistency
                    schedule['everyMs'] = new_every_ms
                else:
                    adjustments.append(f"FAILED to adjust job '{name}' (ID: {job_id}): {output}")
        
        # Check for critical jobs that failed and need immediate retry
        if job_id in ['money-machine', 'f2662e72-8dd4-4548-bcdf-87d67f16bedc']:
            if last_run_status != 'ok':
                # Trigger an immediate run
                cmd = f"openclaw cron run --id {job_id}"
                success, output = run_command(cmd, timeout=30)
                
                if success:
                    retries.append(f"Triggered immediate retry for critical job '{name}' (ID: {job_id})")
                else:
                    retries.append(f"FAILED to trigger retry for critical job '{name}' (ID: {job_id}): {output}")
    
    # Save the updated jobs file if we made any adjustments
    if adjustments:
        save_jobs(data)
        print("Saved updated jobs to", JOBS_FILE)
    
    # Report results
    print("\n=== Auto-Route Failover Report ===")
    if adjustments:
        print("Adjustments made:")
        for adj in adjustments:
            print(f"  - {adj}")
    else:
        print("No schedule adjustments were needed.")
    
    if retries:
        print("\nRetries triggered:")
        for retry in retries:
            print(f"  - {retry}")
    else:
        print("\nNo critical jobs required immediate retry.")
    
    print("\nDone.")

if __name__ == '__main__':
    main()