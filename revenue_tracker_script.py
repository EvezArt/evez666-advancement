#!/usr/bin/env python3
import json
import os
import sys
import glob
import datetime
from pathlib import Path

money_dir = Path('money')
circuits_dir = Path('circuits')  # relative to workspace root

# 1. earnings.json
earnings_file = money_dir / 'earnings.json'
with open(earnings_file) as f:
    earnings = json.load(f)
projected = earnings.get('total', 0)

# 2. actual_revenue.json
actual_file = money_dir / 'actual_revenue.json'
with open(actual_file) as f:
    actual_list = json.load(f)
actual = sum(item.get('amount', 0) for item in actual_list)

# 3. last_revenue_tracker.json
tracker_file = money_dir / 'last_revenue_tracker.json'
if tracker_file.exists():
    with open(tracker_file) as f:
        tracker = json.load(f)
    prev_projected = tracker.get('projected_revenue', {}).get('daily')
    prev_actual = tracker.get('total_actual_revenue')
else:
    prev_projected = None
    prev_actual = None

# 4. circuits
circuit_scripts = list(circuits_dir.glob('*.py'))
circuit_down = []
for script in circuit_scripts:
    if not os.access(script, os.R_OK):
        circuit_down.append('{}: not readable'.format(script.name))
    elif os.path.getsize(script) == 0:
        circuit_down.append('{}: empty file'.format(script.name))

# 5. revenue change alerts
alerts = []
if prev_projected is not None and prev_projected > 0:
    drop = (prev_projected - projected) / prev_projected * 100
    if drop > 10:
        alerts.append('Projected revenue dropped {:.1f}% (from ${:,.2f} to ${:,.2f})'.format(drop, prev_projected, projected))
if prev_actual is not None and prev_actual > 0:
    drop = (prev_actual - actual) / prev_actual * 100
    if drop > 10:
        alerts.append('Actual revenue dropped {:.1f}% (from ${:,.2f} to ${:,.2f})'.format(drop, prev_actual, actual))

# 6. circuit down alerts
if circuit_down:
    alerts.extend(['Circuit issue: {}'.format(issue) for issue in circuit_down])

# 7. report
report = []
report.append('Revenue Tracker Report - {}'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')))
report.append('')
report.append('1. Projected Revenue (earnings.json): ${:,.2f}'.format(projected))
report.append('   - Last updated: {}'.format(earnings.get('last_updated', 'unknown')))
report.append('   - Note: {}'.format(earnings.get('note', '')))
report.append('')
report.append('2. Actual Revenue (actual_revenue.json): ${:,.2f}'.format(actual))
for item in actual_list:
    report.append('   - {}: ${:,.2f} ({}) - {}'.format(
        item.get('source', 'unknown'),
        item.get('amount', 0),
        item.get('ts', 'unknown'),
        item.get('note', '')
    ))
report.append('')
report.append('3. Circuits Status:')
report.append('   - Found {} circuit scripts'.format(len(circuit_scripts)))
for script in circuit_scripts:
    mtime = datetime.datetime.fromtimestamp(os.path.getmtime(script)).strftime('%Y-%m-%d %H:%M')
    report.append('     * {} (last modified: {})'.format(script.name, mtime))
if circuit_down:
    report.append('   - ISSUES DETECTED:')
    for issue in circuit_down:
        report.append('     * {}'.format(issue))
else:
    report.append('   - All circuit scripts present and readable.')
report.append('')
report.append('4. Revenue Change Analysis:')
if prev_projected is not None:
    report.append('   - Previous projected: ${:,.2f}'.format(prev_projected))
    report.append('   - Current projected: ${:,.2f}'.format(projected))
    if prev_projected > 0:
        change = (projected - prev_projected) / prev_projected * 100
        report.append('   - Change: {:+.1f}%'.format(change))
else:
    report.append('   - No previous projected revenue data.')
if prev_actual is not None:
    report.append('   - Previous actual: ${:,.2f}'.format(prev_actual))
    report.append('   - Current actual: ${:,.2f}'.format(actual))
    if prev_actual > 0:
        change = (actual - prev_actual) / prev_actual * 100
        report.append('   - Change: {:+.1f}%'.format(change))
else:
    report.append('   - No previous actual revenue data.')
report.append('')
if alerts:
    report.append('5. ALERTS:')
    for alert in alerts:
        report.append('   - {}'.format(alert))
else:
    report.append('5. No alerts.')
report.append('')

# Output report
print('\n'.join(report))

# 8. Update tracker
tracker_data = {
    'timestamp': datetime.datetime.now().isoformat() + 'Z',
    'earnings': earnings,
    'actual_revenue': actual_list,
    'total_actual_revenue': actual,
    'projected_revenue': {
        'daily': projected,
        'source': 'earnings.json total',
        'note': 'Current projected revenue from earnings.json'
    },
    'alerts': alerts,
    'circuits_checked': len(circuit_scripts)
}
with open(tracker_file, 'w') as f:
    json.dump(tracker_data, f, indent=2)