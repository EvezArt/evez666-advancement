#!/bin/bash
actual_revenue=0
projected_revenue=1800000
achievement=$(echo "scale=2; $actual_revenue * 100 / $projected_revenue" | bc)
circuit_count=$(find circuits -name "*.py" ! -name "*__pycache__*" | wc -l)
running_circuits=0
for script in circuits/*.py; do
    if [ -f "$script" ]; then
        base=$(basename "$script")
        if ps aux | grep -v grep | grep -q "$base"; then
            ((running_circuits++))
        fi
    fi
done
circuits_down=$((circuit_count - running_circuits))
revenue_drop=$(echo "scale=1; ($projected_revenue - $actual_revenue) * 100 / $projected_revenue" | bc)
alert_revenue_drop=$(if (( $(echo "$revenue_drop > 10" | bc -l) )); then echo "YES"; else echo "NO"; fi)
alert_circuits_down=$(if [ "$circuits_down" -gt 0 ]; then echo "YES"; else echo "NO"; fi)
report="Revenue Tracker Report - $(date -u '+%A, %B %d, %Y - %H:%M UTC')
==================================================
Actual Revenue: \$$actual_revenue
Projected Revenue: \$$projected_revenue/day
Achievement: $achievement%
Circuits Status: $running_circuits\(\%\) of $circuit_count circuits running ($circuits_down down).

ALERTS:"
if [ "$alert_revenue_drop" = "YES" ]; then
    report="$report
  [CRITICAL] Real revenue: \$$actual_revenue (per earnings.json) vs Projected revenue: \$$projected_revenue/day. Revenue drop: $revenue_drop% (exceeds 10% alert threshold)."
fi
if [ "$alert_circuits_down" = "YES" ]; then
    report="$report
  [WARNING] $circuits_down of $circuit_count revenue circuits are not running."
fi
echo -e "$report" > money/revenue_tracker_latest.txt
echo -e "\n---\n$(date -u '+%Y-%m-%d %H:%M:%S UTC')
$report" >> money/revenue_tracker.log
echo "Revenue tracker report updated."
