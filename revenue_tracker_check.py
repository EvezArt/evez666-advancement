import json
import os
from datetime import datetime, timedelta

# 1) Check earnings.json
earnings_path = '/root/.openclaw/workspace/money/earnings.json'
with open(earnings_path) as f:
    earnings = json.load(f)
projected_total = earnings['total']
note = earnings.get('note', '')
last_updated = earnings.get('last_updated')

# 2) Check actual_revenue.json
actual_path = '/root/.openclaw/workspace/money/actual_revenue.json'
with open(actual_path) as f:
    actual_list = json.load(f)
actual_total = sum(item['amount'] for item in actual_list)

# 3) Check circuits/ for updates
circuits_dir = '/root/.openclaw/workspace/circuits'
circuit_files = [f for f in os.listdir(circuits_dir) if f.endswith('.py')]
total_circuits = len(circuit_files)
updated_circuits = []
one_day_ago = datetime.now() - timedelta(days=1)
for f in circuit_files:
    fpath = os.path.join(circuits_dir, f)
    mtime = datetime.fromtimestamp(os.path.getmtime(fpath))
    if mtime > one_day_ago:
        updated_circuits.append(f)

# 4) Report total projected revenue
print(f'Projected Revenue: ${projected_total:.2f}')
if note:
    print(f'Note: {note}')
print(f'Actual Revenue: ${actual_total:.2f}')
print(f'Circuits: {total_circuits} total, {len(updated_circuits)} updated in last 24h')
if updated_circuits:
    print('Updated circuits:', ', '.join(updated_circuits))

# 5) Alert if any circuit is down or revenue dropped >10%
# We don't have a way to check circuit status, so we skip circuit down alert.
# For revenue drop: we need a previous value. We'll use the note in earnings.json to get previous projected revenue.
import re
prev_match = re.search(r'\$?(\d+\.\d+)', note)
if prev_match:
    prev_projected = float(prev_match.group(1))
    if prev_projected > 0:
        drop_pct = ((prev_projected - projected_total) / prev_projected) * 100
        print(f'Projected revenue change: {drop_pct:.1f}% (from ${prev_projected:.2f} to ${projected_total:.2f})')
        if drop_pct > 10:
            print('ALERT: Projected revenue dropped >10%!')
    else:
        print('Note: Previous projected revenue was zero or negative, cannot calculate drop.')
else:
    print('No previous projected revenue found in note.')

# Check actual revenue drop? We don't have historical actual revenue stored.
print('No historical actual revenue data for drop comparison.')