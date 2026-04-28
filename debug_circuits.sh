#!/bin/bash
circuits_json='[]'
for script in alert_empire.py backup_god.py; do
    if [ -f "money/circuits/$script" ]; then
        updated=$(stat -c %Y "money/circuits/$script" | xargs -I{} date -d @{} -u +"%Y-%m-%dT%H:%M:%SZ")
        running=$(ps aux | grep -v grep | grep -c "$script" || echo 0)
        status="RUNNING"
        if [ $running -eq 0 ]; then
            status="DOWN"
        fi
        echo "Processing $script: updated=$updated, running=$running, status=$status"
        circuits_json=$(echo "$circuits_json" | jq --arg name "$script" --arg updated "$updated" --arg status "$status" '. + [{"name": $name, "updated": $updated, "status": $status}]')
        echo "After jq: $circuits_json"
    fi
done
echo "Final circuits_json: $circuits_json"
