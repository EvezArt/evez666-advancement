#!/usr/bin/env python3
import json
import os
from datetime import datetime

# Load actual revenue
actual_file = '/root/.openclaw/workspace/money/actual_revenue.json'
if os.path.exists(actual_file):
    with open(actual_file) as f:
        actual_data = json.load(f)
    actual_total = sum(entry.get('amount', 0) for entry in actual_data)
else:
    actual_total = 0
    actual_data = []

# Projected revenue from USER.md (hardcoded for now)
projected_daily = 1_800_000  # $1.8M/day

# Calculate drop percentage
if projected_daily > 0:
    drop_pct = (projected_daily - actual_total) / projected_daily * 100
else:
    drop_pct = 0

# Check circuits directory
circuits_dir = '/root/.openclaw/workspace/circuits'
circuit_files = []
if os.path.isdir(circuits_dir):
    circuit_files = [f for f in os.listdir(circuits_dir) if f.endswith('.py')]

# Determine if any circuit is down (simplified: no payment processor)
payment_connected = False  # based on notes in actual_revenue.json

# Generate report
report = []
report.append('=' * 60)
report.append('REVENUE TRACKER REPORT')
report.append(f'Timestamp: {datetime.now().isoformat()}')
report.append('-' * 60)
report.append(f'Projected Daily Revenue: ${projected_daily:,.2f}')
report.append(f'Actual Total Revenue: ${actual_total:,.2f}')
report.append(f'Revenue Drop: {drop_pct:.1f}%')
report.append('-' * 60)
report.append('CIRCUITS STATUS:')
report.append(f'  Number of circuits found: {len(circuit_files)}')
for cf in circuit_files:
    report.append(f'  - {cf}')
report.append('')
report.append('PAYMENT PROCESSOR CONNECTED: {}'.format('YES' if payment_connected else 'NO'))
report.append('')
if actual_total == 0:
    report.append('NOTE: No real revenue detected. All revenue figures are fictional until payment processor is integrated.')
elif drop_pct > 10:
    report.append('ALERT: Revenue dropped more than 10% compared to projected!')
else:
    report.append('Revenue within expected range.')

report.append('=' * 60)
report_text = '\n'.join(report)

# Print to stdout
print(report_text)

# Write to report file
report_dir = '/root/.openclaw/workspace/money'
os.makedirs(report_dir, exist_ok=True)
report_file = os.path.join(report_dir, f'revenue_report_{datetime.now().strftime("%Y-%m-%d_%H-%M")}.txt')
with open(report_file, 'w') as f:
    f.write(report_text)
print(f'Report written to: {report_file}')