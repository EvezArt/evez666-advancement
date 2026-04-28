#!/bin/bash
PROJECTED=1800000
actual_earnings=$(jq '.total' money/earnings.json)
actual_sum=$(jq '[.[] | .amount] | add' money/actual_revenue.json)
echo "Revenue Tracker Report"
echo "===================="
echo "Timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo ""
echo "Projected Revenue (daily): \$$PROJECTED"
echo "Actual Revenue (earnings.json): \$$actual_earnings"
echo "Actual Revenue (sum of actual_revenue.json): \$$actual_sum"
echo ""
echo "Circuits Checked: 7"
any_down=0
for script in alert_empire.py backup_god.py cloud_forge.py content_amplifier.py customer_closer.py data_factory.py the_money_spin.py; do
  if [ -f "money/circuits/$script" ]; then
    updated=$(stat -c %Y "money/circuits/$script" | xargs -I{} date -d @{} -u +"%Y-%m-%dT%H:%M:%SZ")
    running=$(ps aux | grep -v grep | grep -c "$script" || echo 0)
    status="[RUNNING]"
    if [ $running -eq 0 ]; then
      status="[DOWN]"
      any_down=1
    fi
    echo "  - $script (updated $updated) $status"
  fi
done
echo ""
echo "Alerts:"
drop_earnings=$(echo "scale=2; ($PROJECTED - $actual_earnings) * 100 / $PROJECTED" | bc -l)
drop_sum=$(echo "scale=2; ($PROJECTED - $actual_sum) * 100 / $PROJECTED" | bc -l)
if (( $(echo "$drop_earnings > 10" | bc -l) )); then
  echo "  ! REVENUE ALERT: Actual revenue is \$$actual_earnings (per earnings.json) vs projected \$$PROJECTED/day - $drop_earnings% drop (>10% threshold)"
fi
if (( $(echo "$drop_sum > 10" | bc -l) )); then
  echo "  ! REVENUE ALERT: Actual revenue tracked is \$$actual_sum (from actual_revenue.json) vs projected \$$PROJECTED/day - $drop_sum% drop (>10% threshold)"
fi
if [ $any_down -eq 1 ]; then
  echo "  ! CIRCUIT ALERT: At least one circuit is down (see above)"
fi
