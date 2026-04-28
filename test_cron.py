import json

with open('cron.json') as f:
    data = json.load(f)

print(f"Total jobs: {data['total']}")

ok_jobs = 0
error_jobs = 0

for job in data['jobs']:
    status = job['state']['lastRunStatus']
    if status == 'ok':
        ok_jobs += 1
    elif status == 'error':
        error_jobs += 1

print(f"OK jobs: {ok_jobs}")
print(f"Error jobs: {error_jobs}")

if data['total'] > 0:
    health_percent = int((ok_jobs / data['total']) * 100)
    print(f"Health: {health_percent}% OK ({ok_jobs}/{data['total']}), {error_jobs} errors")
else:
    print("No jobs found")