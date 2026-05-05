import json
import os
from datetime import datetime, timedelta

# 1. earnings.json
with open('money/earnings.json') as f:
    earnings = json.load(f)
earnings_total = earnings['total']

# 2. actual_revenue.json
with open('money/actual_revenue.json') as f:
    actual_list = json.load(f)
actual_total = sum(item['amount'] for item in actual_list)

# 3. circuits
circuit_dir = 'circuits'
circuit_files = [f for f in os.listdir(circuit_dir) if f.endswith('.py')]
circuit_status = []
stale_threshold = datetime.now() - timedelta(days=2)
stale_circuits = []
for cf in circuit_files:
    path = os.path.join(circuit_dir, cf)
    mtime = datetime.fromtimestamp(os.path.getmtime(path))
    circuit_status.append((cf, mtime.isoformat()))
    if mtime < stale_threshold:
        stale_circuits.append(cf)

# 4. projected revenue from revenue_tracker_report.json
with open('money/revenue_tracker_report.json') as f:
    revenue_report = json.load(f)
projected = revenue_report['projected_revenue_daily']
actual_from_report = revenue_report['actual_revenue']

# Calculate drop
if projected > 0:
    drop_percent = (1 - actual_from_report / projected) * 100
else:
    drop_percent = 0

# Alerts
alerts = []
if drop_percent > 10:
    alerts.append('Revenue dropped {:.2f}% (actual {} vs projected {}/day)'.format(drop_percent, actual_from_report, projected))
if stale_circuits:
    alerts.append('Stale circuits (not updated in >2 days): ' + ', '.join(stale_circuits))

# Output
print('=== Revenue Tracker Report ===')
print('Time: {}'.format(datetime.now().isoformat()))
print('Earnings total (from earnings.json): {}'.format(earnings_total))
print('Actual revenue total (from actual_revenue.json): {}'.format(actual_total))
print('Actual revenue (from report): {}'.format(actual_from_report))
print('Projected revenue (daily): {}'.format(projected))
print('Drop percent: {:.2f}%'.format(drop_percent))
print('')
print('Circuit status:')
for cf, mtime in circuit_status:
    print('  {}: {}'.format(cf, mtime))
if stale_circuits:
    print('  STALE: ' + ', '.join(stale_circuits))
else:
    print('  All circuits updated within last 2 days.')
print('')
if alerts:
    print('ALERTS:')
    for alert in alerts:
        print('  - {}'.format(alert))
else:
    print('No alerts.')