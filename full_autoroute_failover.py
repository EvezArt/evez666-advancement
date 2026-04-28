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
    print("=== Auto-Route Failover ===")
    print(f"Time: {time.ctime()}")
    
    # Step 1: List all cron jobs (we'll load from file)
    data = load_jobs()
    jobs = data.get('jobs', [])
    print(f"\n1) Loaded {len(jobs)} cron jobs from {JOBS_FILE}")
    
    adjustments = []
    retries = []
    
    # Step 2: For any job with consecutiveErrors > 3, adjust schedule to run slower (multiply interval by 1.5)
    print("\n2) Checking for jobs with consecutiveErrors > 3...")
    for job in jobs:
        job_id = job.get('id')
        name = job.get('name')
        state = job.get('state', {})
        schedule = job.get('schedule', {})
        consecutive_errors = state.get('consecutiveErrors', 0)
        
        if consecutive_errors > 3 and schedule.get('kind') == 'every':
            every_ms = schedule.get('everyMs', 0)
            if every_ms > 0:
                new_every_ms = int(every_ms * 1.5)
                human_interval = ms_to_human(new_every_ms)
                
                # Update the schedule in memory
                schedule['everyMs'] = new_every_ms
                # Reset anchor to now to avoid drift
                schedule['anchorMs'] = int(time.time() * 1000)
                job['updatedAtMs'] = int(time.time() * 1000)
                
                adjustments.append({
                    'job_id': job_id,
                    'name': name,
                    'old_interval_ms': every_ms,
                    'new_interval_ms': new_every_ms,
                    'old_interval_human': ms_to_human(every_ms),
                    'new_interval_human': human_interval
                })
                print(f"   - Will adjust '{name}' (ID: {job_id}): {every_ms}ms -> {new_every_ms}ms ({human_interval})")
    
    # Step 3: For jobs with OK status that ran recently, keep as-is (we do nothing, just note)
    print("\n3) Jobs with OK status that ran recently are kept as-is (no action needed).")
    
    # Step 4: If a critical job (money-machine, revenue loop) fails, attempt one immediate retry
    critical_job_ids = ['money-machine', 'f2662e72-8dd4-4548-bcdf-87d67f16bedc']
    print("\n4) Checking critical jobs for failures...")
    for job in jobs:
        job_id = job.get('id')
        if job_id in critical_job_ids:
            name = job.get('name')
            state = job.get('state', {})
            last_run_status = state.get('lastRunStatus')
            consecutive_errors = state.get('consecutiveErrors', 0)
            
            if last_run_status != 'ok':
                print(f"   - Critical job '{name}' (ID: {job_id}) has lastRunStatus: {last_run_status} (errors: {consecutive_errors})")
                # Trigger an immediate run
                cmd = f"openclaw cron run --id {job_id}"
                success, output = run_command(cmd, timeout=30)
                
                if success:
                    retries.append(f"Triggered immediate retry for critical job '{name}' (ID: {job_id})")
                    print(f"     -> Successfully triggered retry.")
                else:
                    retries.append(f"FAILED to trigger retry for critical job '{name}' (ID: {job_id}): {output}")
                    print(f"     -> Failed to trigger retry: {output}")
            else:
                print(f"   - Critical job '{name}' (ID: {job_id}) is OK (lastRunStatus: ok, errors: {consecutive_errors})")
    
    # Save the updated jobs file if we made any adjustments
    if adjustments:
        save_jobs(data)
        print(f"\n5) Saved updated jobs to {JOBS_FILE} and {BACKUP_FILE}")
    else:
        print("\n5) No schedule adjustments were needed.")
    
    # Report results
    print("\n=== RESULTS ===")
    if adjustments:
        print("Adjustments made:")
        for adj in adjustments:
            print(f"  - Job: {adj['name']} (ID: {adj['job_id']})")
            print(f"    Interval: {adj['old_interval_human']} ({adj['old_interval_ms']}ms) -> {adj['new_interval_human']} ({adj['new_interval_ms']}ms)")
    else:
        print("No schedule adjustments were needed.")
    
    if retries:
        print("\nRetries triggered:")
        for retry in retries:
            print(f"  - {retry}")
    else:
        print("\nNo critical jobs required immediate retry.")
    
    print("\nAuto-route failover completed.")

if __name__ == '__main__':
    main()