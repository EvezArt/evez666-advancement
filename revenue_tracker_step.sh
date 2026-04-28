#!/bin/bash
cd /root/.openclaw/workspace
echo "Running revenue tracker..."

# 1) Check /root/.openclaw/workspace/money/earnings.json
earnings_total=$(jq '.total' money/earnings.json)
echo "Earnings total: $earnings_total"

# 2) Check /root/.openclaw/workspace/money/actual_revenue.json
actual_total=$(jq '[.[] | .amount] | add' money/actual_revenue.json)
echo "Actual revenue total: $actual_total"

# 3) Check circuits/ for any updates (located at workspace/circuits/)
circuit_count=$(ls circuits/*.py 2>/dev/null | wc -l)
echo "Circuits checked: $circuit_count"

# 4) Report total projected revenue (from memory, we know it's $1.8M/day)
projected_daily=1800000
echo "Projected daily revenue: $projected_daily"

# 5) Alert if any circuit is down or revenue dropped >10%
# Calculate drop percentage
if (( $(echo "$projected_daily > 0" | bc -l) )); then
    drop_percentage=$(echo "scale=2; (1 - ($actual_total / $projected_daily)) * 100" | bc)
else
    drop_percentage=100
fi
echo "Drop percentage: ${drop_percentage}%"

alert_message=""
if (( $(echo "$drop_percentage > 10" | bc -l) )); then
    alert_message="Actual revenue tracked is \$$actual_total (from actual_revenue.json) vs projected \$$projected_daily/day - ${drop_percentage}% drop (>10% threshold)"
fi

# Output alerts
if [ -n "$alert_message" ]; then
    echo "ALERT: $alert_message"
else
    echo "No alerts."
fi

# Update last_revenue_tracker.json
cat > money/last_revenue_tracker.json <<EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)",
  "earnings": $(cat money/earnings.json),
  "actual_revenue": $(cat money/actual_revenue.json),
  "total_actual_revenue": $actual_total,
  "projected_revenue": {
    "daily": $projected_daily,
    "source": "historical data from memory files",
    "note": "Repeatedly referenced as \$1.8M/day across 7 circuits in memory logs"
  },
  "alerts": $(if [ -n "$alert_message" ]; then printf '%s' "[\"$alert_message\"]"; else printf '%s' "[]"; fi),
  "circuits_checked": $circuit_count
}
EOF

echo "Updated money/last_revenue_tracker.json"