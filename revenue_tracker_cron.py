#!/usr/bin/env python3
import json
import datetime
import os
import subprocess

def main():
    # Get current time in UTC and Los_Angeles
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    try:
        import pytz
        la_tz = pytz.timezone('America/Los_Angeles')
        la_now = utc_now.astimezone(la_tz)
        date_local = la_now.strftime('%A, %B %dth, %Y - %I:%M %p (%Z)')
    except:
        # Fallback if pytz not available
        date_local = utc_now.strftime('%A, %B %dth, %Y - %I:%M %p (UTC)')

    # Check earnings.json (this is what we compare against projected for revenue drop)
    earnings_path = '/root/.openclaw/workspace/money/earnings.json'
    if os.path.exists(earnings_path):
        with open(earnings_path, 'r') as f:
            earnings_data = json.load(f)
    else:
        earnings_data = {'total': 0, 'sources': [], 'last_updated': '', 'note': 'File not found'}

    earnings_total = float(earnings_data.get('total', 0))

    # Check actual_revenue.json (for reporting)
    actual_path = '/root/.openclaw/workspace/money/actual_revenue.json'
    if os.path.exists(actual_path):
        with open(actual_path, 'r') as f:
            actual_data = json.load(f)
    else:
        actual_data = []

    actual_total = 0
    if isinstance(actual_data, list):
        for entry in actual_data:
            if isinstance(entry, dict) and 'amount' in entry:
                actual_total += float(entry['amount'])
    else:
        if isinstance(actual_data, dict) and 'amount' in actual_data:
            actual_total = float(actual_data['amount'])

    # Check circuits directory for running processes
    circuits_dir = '/root/.openclaw/workspace/circuits'
    circuits_scripts = [
        'data_factory.py',
        'content_amplifier.py',
        'alert_empire.py',
        'customer_closer.py',
        'cloud_forge.py',
        'the_money_spin.py',
        'backup_god.py'
    ]
    running = []
    for script in circuits_scripts:
        try:
            output = subprocess.check_output(['pgrep', '-f', script], stderr=subprocess.DEVNULL, text=True)
            if output.strip():
                running.append(script)
        except subprocess.CalledProcessError:
            pass

    circuits_status = {
        'directory': circuits_dir,
        'directory_exists': os.path.exists(circuits_dir),
        'known_circuit_scripts': circuits_scripts,
        'scripts_found_locations': {},
        'running_processes': running,
        'status': 'All circuits appear to be down (no running processes found for any circuit scripts).' if len(running) == 0 else f'{len(running)} circuits running: {", ".join(running)}'
    }

    # Projected revenue from historical data
    projected_daily = 1800000

    # Determine alerts
    alerts = []
    
    # Check for revenue drop >10% using earnings.json total (real revenue)
    if projected_daily > 0:
        revenue_drop_percent = ((projected_daily - earnings_total) / projected_daily) * 100
        if revenue_drop_percent > 10:
            alerts.append({
                'type': 'REVENUE_DROP',
                'severity': 'CRITICAL',
                'message': f'Real revenue: ${earnings_total:.2f} (per earnings.json) vs Projected revenue: ${projected_daily:,}/day. Revenue drop: {revenue_drop_percent:.1f}% (exceeds 10% alert threshold).',
                'details': 'Payment blockade active - requires external action to connect payment processors.'
            })
    
    # Check for circuits down
    if len(running) < len(circuits_scripts):
        alerts.append({
            'type': 'CIRCUIT_DOWN',
            'severity': 'WARNING',
            'message': f'{len(circuits_scripts) - len(running)} of {len(circuits_scripts)} revenue circuits are not running.',
            'details': f'Running circuits: {", ".join(running) if running else "None"}'
        })

    # Build the report
    report = {
        'timestamp': utc_now.isoformat(),
        'date_local': date_local,
        'earnings_check': {
            'file': earnings_path,
            'total': earnings_data.get('total', 0),
            'sources': earnings_data.get('sources', []),
            'last_updated': earnings_data.get('last_updated', ''),
            'note': earnings_data.get('note', '')
        },
        'actual_revenue_check': {
            'file': actual_path,
            'entries': actual_data if isinstance(actual_data, list) else [actual_data] if isinstance(actual_data, dict) else [],
            'total_tracked': actual_total,
            'note': 'All amounts are simulated/test; no real revenue.' if actual_total > 0 else 'No real revenue.'
        },
        'circuits_status': circuits_status,
        'projected_revenue': {
            'daily': projected_daily,
            'note': 'Historical data from memory files: $1.8M/day across 7 circuits'
        },
        'alerts': alerts,
        'summary': {
            'status': 'ERROR' if len(alerts) > 0 and any(a['severity'] == 'CRITICAL' for a in alerts) else 'WARNING' if len(alerts) > 0 else 'OK',
            'description': 'Revenue system non-functional' if earnings_total == 0 else 'Revenue system operational',
            'actual_daily_revenue': earnings_total,  # Use earnings total for summary
            'projected_daily_revenue': projected_daily,
            'revenue_achievement_percent': (earnings_total / projected_daily * 100) if projected_daily > 0 else 0,
            'action_required': 'Restart revenue circuits and connect payment processors' if earnings_total == 0 else 'Monitor revenue streams'
        }
    }

    # Write the report
    with open('/root/.openclaw/workspace/money/revenue_tracker_report.json', 'w') as f:
        json.dump(report, f, indent=2)

    # Also write a latest.txt summary
    latest_path = '/root/.openclaw/workspace/money/revenue_tracker_latest.txt'
    with open(latest_path, 'w') as f:
        f.write(f"Revenue Tracker Report - {date_local}\n")
        f.write('='*50 + '\n')
        f.write(f"Actual Revenue: ${earnings_total:.2f}\n")
        f.write(f"Projected Revenue: ${projected_daily:,}/day\n")
        f.write(f"Achievement: {report['summary']['revenue_achievement_percent']:.2f}%\n")
        f.write(f"Circuits Status: {circuits_status['status']}\n")
        if alerts:
            f.write('\nALERTS:\n')
            for alert in alerts:
                f.write(f"  [{alert['severity']}] {alert['message']}\n")
        else:
            f.write('\nNo alerts.\n')

    # Append to log
    log_path = '/root/.openclaw/workspace/money/revenue_tracker.log'
    with open(log_path, 'a') as f:
        f.write(f"[{date_local}] Revenue tracker run. Actual: ${earnings_total:.2f}, Projected: ${projected_daily:,}/day, Alerts: {len(alerts)}\n")

if __name__ == '__main__':
    main()