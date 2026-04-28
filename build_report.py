import json
import os
from datetime import datetime

print("Loading cron data...")
with open('/root/.openclaw/workspace/cron.json') as f:
    cron_data = json.load(f)

print("Loading earnings...")
with open('/root/.openclaw/workspace/money/earnings.json') as f:
    earnings = json.load(f)

print("Checking actual revenue...")
actual_revenue_path = '/root/.openclaw/workspace/money/actual_revenue.json'
if os.path.exists(actual_revenue_path):
    with open(actual_revenue_path) as f:
        actual_revenue = json.load(f)
else:
    actual_revenue = {}

print("Checking revenue tracker latest...")
revenue_tracker_latest = '/root/.openclaw/workspace/money/revenue_tracker_latest.txt'
if os.path.exists(revenue_tracker_latest):
    with open(revenue_tracker_latest) as f:
        revenue_tracker_latest_content = f.read()
else:
    revenue_tracker_latest_content = ""

print("Loading milestones...")
milestones = ''
if os.path.exists('/root/.openclaw/workspace/memory/milestones.md'):
    with open('/root/.openclaw/workspace/memory/milestones.md') as f:
        milestones = f.read()

print("Checking errors from last hour...")
now_ms = int(datetime.now().timestamp() * 1000)
one_hour_ago_ms = now_ms - (60 * 60 * 1000)
errors = []
for job in cron_data['jobs']:
    state = job['state']
    consecutive_errors = state.get('consecutiveErrors', 0)
    last_run_at_ms = state.get('lastRunAtMs', 0)
    if consecutive_errors > 0 and last_run_at_ms > one_hour_ago_ms:
        errors.append({
            'job': job['name'],
            'errors': consecutive_errors,
            'last_error': state.get('lastError', 'unknown'),
            'last_run_ms': last_run_at_ms
        })

print("Building report...")
report = []
report.append(f"# Mem0 Auto-Memory Report")
report.append(f"**Timestamp**: {datetime.now().isoformat()}")
report.append(f"")
report.append(f"## 1. Cron Job Statuses")
report.append(f"")
for job in cron_data['jobs']:
    report.append(f"### {job['name']}")
    report.append(f"- ID: {job['id']}")
    report.append(f"- Enabled: {job['enabled']}")
    report.append(f"- Last Run Status: {job['state'].get('lastRunStatus', 'unknown')}")
    report.append(f"- Last Run At: {job['state'].get('lastRunAtMs', 'unknown')}")
    if job['state'].get('lastError'):
        report.append(f"- Last Error: {job['state']['lastError']}")
    report.append(f"- Consecutive Errors: {job['state'].get('consecutiveErrors', 0)}")
    report.append(f"")
report.append(f"")
report.append(f"## 2. Revenue Circuit States")
report.append(f"")
report.append(f"### Earnings.json")
report.append(f"```json")
report.append(json.dumps(earnings, indent=2))
report.append(f"```")
report.append(f"")
report.append(f"### Actual Revenue.json")
report.append(f"```json")
report.append(json.dumps(actual_revenue, indent=2))
report.append(f"```")
report.append(f"")
if revenue_tracker_latest_content:
    report.append(f"### Revenue Tracker Latest")
    report.append(f"```")
    report.append(revenue_tracker_latest_content)
    report.append(f"```")
    report.append(f"")
report.append(f"## 3. Errors from Last Hour")
report.append(f"")
if errors:
    for err in errors:
        report.append(f"- **Job**: {err['job']}")
        report.append(f"  - Errors: {err['errors']}")
        report.append(f"  - Last Error: {err['last_error']}")
        report.append(f"  - Last Run Ms: {err['last_run_ms']}")
else:
    report.append(f"No errors in the last hour.")
report.append(f"")
report.append(f"## 4. Key Decisions Made")
report.append(f"")
key_decisions = [
    'Relying on file-based memory system due to Mem0/billing issues',
    'Payment processors remain disconnected, blocking revenue',
    'EVEZ Studio services are operational',
    'Auto-route failover adjusts schedules for failing jobs'
]
for decision in key_decisions:
    report.append(f"- {decision}")
report.append(f"")
report.append(f"## 5. Milestones Snapshot (last 500 chars)")
report.append(f"")
if milestones:
    if len(milestones) > 500:
        report.append(f"```")
        report.append(milestones[-500:])
        report.append(f"```")
    else:
        report.append(f"```")
        report.append(milestones)
        report.append(f"```")
else:
    report.append(f"No milestones found.")

print("Writing to file...")
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
filename = f"/root/.openclaw/workspace/memory/mem0_auto_save_{timestamp}.md"
with open(filename, 'w') as f:
    f.write('\n'.join(report))

print(f"Saved report to {filename}")