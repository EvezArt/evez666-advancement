import json
import os
from datetime import datetime

# Load actual revenue
actual_file = 'money/actual_revenue.json'
with open(actual_file) as f:
    actual_data = json.load(f)
total_actual = sum(item['amount'] for item in actual_data)
print('Total actual revenue:', total_actual)

# Load earnings
earnings_file = 'money/earnings.json'
try:
    with open(earnings_file) as f:
        earnings_data = json.load(f)
    earnings_total = earnings_data.get('total', 0)
except:
    earnings_total = 0
print('Earnings total:', earnings_total)

# Projected revenue from memory or last run
# We'll try to read from last_revenue_tracker.json
last_file = 'money/last_revenue_tracker.json'
if os.path.exists(last_file):
    with open(last_file) as f:
        last_data = json.load(f)
    projected_daily = last_data.get('projected_revenue', {}).get('daily', 0)
else:
    projected_daily = 0
print('Projected daily revenue:', projected_daily)

# Check circuits
circuits_dir = 'money/circuits'
if not os.path.exists(circuits_dir):
    circuits_dir = 'circuits'
circuit_files = []
if os.path.exists(circuits_dir):
    circuit_files = [f for f in os.listdir(circuits_dir) if f.endswith('.py')]
print('Number of circuit scripts:', len(circuit_files))
for cf in circuit_files:
    print('  -', cf)

# Determine alerts
alerts = []
if projected_daily > 0:
    drop_pct = (projected_daily - total_actual) / projected_daily * 100
    if drop_pct > 10:
        alerts.append('Revenue dropped {:.2f}% (actual {} vs projected {}/day)'.format(drop_pct, total_actual, projected_daily))
else:
    # If no projected, but we have actual, still note if actual is low?
    pass

# Check for circuit issues: we can do a simple syntax check
for cf in circuit_files:
    path = os.path.join(circuits_dir, cf)
    try:
        with open(path) as f:
            compile(f.read(), path, 'exec')
    except SyntaxError as e:
        alerts.append('Circuit {} has syntax error: {}'.format(cf, e))
    except Exception as e:
        alerts.append('Circuit {} error reading: {}'.format(cf, e))

# Prepare report
report = {
    'timestamp': datetime.utcnow().isoformat() + 'Z',
    'actual_revenue': total_actual,
    'earnings': earnings_total,
    'projected_revenue_daily': projected_daily,
    'circuits_count': len(circuit_files),
    'circuits': circuit_files,
    'alerts': alerts
}

# Write JSON report
report_file = 'money/revenue_tracker_report.json'
with open(report_file, 'w') as f:
    json.dump(report, f, indent=2)
print('Report written to', report_file)

# Write text summary
text_file = 'money/revenue_tracker_report.txt'
with open(text_file, 'w') as f:
    f.write('Revenue Tracker Report\n')
    f.write('====================\n')
    f.write('Timestamp: {}\n'.format(report['timestamp']))
    f.write('Actual Revenue: ${:.2f}\n'.format(total_actual))
    f.write('Earnings Total: ${:.2f}\n'.format(earnings_total))
    f.write('Projected Daily Revenue: ${:.2f}\n'.format(projected_daily))
    f.write('Circuits Checked: {}\n'.format(len(circuit_files)))
    for cf in circuit_files:
        f.write('  - {}\n'.format(cf))
    if alerts:
        f.write('\nALERTS:\n')
        for alert in alerts:
            f.write('  - {}\n'.format(alert))
    else:
        f.write('\nNo alerts.\n')
print('Text report written to', text_file)

# Update latest.txt
latest_file = 'money/revenue_tracker_latest.txt'
latest_content = '{:.2f} actual vs {:.2f} projected'.format(total_actual, projected_daily)
if alerts:
    latest_content += ' | ALERT: {}'.format(alerts[0])
with open(latest_file, 'w') as f:
    f.write(latest_content)
print('Latest updated:', latest_file)