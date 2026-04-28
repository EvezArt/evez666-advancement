#!/bin/bash
PROJECTED=1800000
actual_earnings=$(jq '.total' money/earnings.json)
actual_sum=$(jq '[.[] | .amount] | add' money/actual_revenue.json)
drop_earnings=$(echo "scale=2; ($PROJECTED - $actual_earnings) * 100 / $PROJECTED" | bc -l)
drop_sum=$(echo "scale=2; ($PROJECTED - $actual_sum) * 100 / $PROJECTED" | bc -l)

# Build alerts array
alerts_json='[]'
if (( $(echo "$drop_earnings > 10" | bc -l) )); then
    alerts_json=$(echo "$alerts_json" | jq --arg msg "Actual revenue is \$$actual_earnings (per earnings.json) vs projected \$$PROJECTED/day - $drop_earnings% drop (>10% threshold)" '. + [$msg]')
fi
if (( $(echo "$drop_sum > 10" | bc -l) )); then
    alerts_json=$(echo "$alerts_json" | jq --arg msg "Actual revenue tracked is \$$actual_sum (from actual_revenue.json) vs projected \$$PROJECTED/day - $drop_sum% drop (>10% threshold)" '. + [$msg]')
fi

# Build circuits status
circuits_json='[]'
any_down=0
for script in alert_empire.py backup_god.py cloud_forge.py content_amplifier.py customer_closer.py data_factory.py the_money_spin.py; do
    if [ -f "money/circuits/$script" ]; then
        updated=$(stat -c %Y "money/circuits/$script" | xargs -I{} date -d @{} -u +"%Y-%m-%dT%H:%M:%SZ")
        running=$(ps aux | grep -v grep | grep -c "$script" || echo 0)
        status="RUNNING"
        if [ $running -eq 0 ]; then
            status="DOWN"
            any_down=1
        fi
        circuits_json=$(echo "$circuits_json" | jq --arg name "$script" --arg updated "$updated" --arg status "$status" '. + [{"name": $name, "updated": $updated, "status": $status}]')
    fi
done

if [ $any_down -eq 1 ]; then
    alerts_json=$(echo "$alerts_json" | jq --arg msg "At least one circuit is down (see above)" '. + [$msg]')
fi

# Generate final JSON
cat > money/last_revenue_tracker.json << EOF_JSON
{
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "earnings": $(cat money/earnings.json),
  "actual_revenue": $(cat money/actual_revenue.json),
  "circuits": {
    "directory": "/root/.openclaw/workspace/money/circuits",
    "scripts": [
      "alert_empire.py",
      "backup_god.py",
      "cloud_forge.py",
      "content_amplifier.py",
      "customer_closer.py",
      "data_factory.py",
      "the_money_spin.py"
    ],
    "status": $circuits_json
  },
  "projected_revenue": {
    "daily": $PROJECTED,
    "source": "historical data from memory files",
    "note": "Repeatedly referenced as \$1.8M/day across 7 circuits in memory logs"
  },
  "alerts": $alerts_json
}
EOF_JSON
