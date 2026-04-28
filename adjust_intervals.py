import json
import time
import os

JOBS_FILE = '/root/.openclaw/cron/jobs.json'
BACKUP_FILE = '/root/.openclaw/cron/jobs.json.backup.' + str(int(time.time()))

def ms_to_human(ms):
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
    if seconds > 0 and not parts:
        parts.append(f"{seconds}s")
    if not parts:
        return "0s"
    return "".join(parts)

def main():
    # Backup
    os.system(f"cp {JOBS_FILE} {BACKUP_FILE}")
    
    with open(JOBS_FILE, 'r') as f:
        data = json.load(f)
    
    jobs = data.get('jobs', [])
    now_ms = int(time.time() * 1000)
    
    adjustments = []
    
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
                schedule['everyMs'] = new_every_ms
                schedule['anchorMs'] = now_ms  # reset anchor to now
                job['updatedAtMs'] = now_ms
                adjustments.append((name, job_id, every_ms, new_every_ms))
    
    if adjustments:
        with open(JOBS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        print("Updated jobs.json")
        for name, job_id, old, new in adjustments:
            print(f"  - {name} (ID: {job_id}): {old}ms -> {new}ms ({ms_to_human(new)})")
    else:
        print("No adjustments needed.")

if __name__ == '__main__':
    main()