#!/bin/bash
# NL Scheduler wrapper - creates cron jobs from natural language

TEXT="$1"

if [ -z "$TEXT" ]; then
    echo "Usage: nl-scheduler <task description>"
    echo "Examples:"
    echo "  nl-scheduler 'every morning at 8am check my emails'"
    echo "  nl-scheduler 'every 5 minutes sync my files'"
    echo "  nl-scheduler 'every week on monday generate a report'"
    exit 1
fi

echo "Parsing: $TEXT"
echo ""

# Simple parsing in bash for now
if echo "$TEXT" | grep -qi "every.*minute"; then
    INTERVAL=$(echo "$TEXT" | grep -oP '\d+(?=\s*minute)' || echo "5")
    echo "Schedule: every $INTERVAL minutes"
    echo "Action: $(echo "$TEXT" | sed 's/every.*minutes//g' | xargs)"
elif echo "$TEXT" | grep -qi "every.*hour"; then
    echo "Schedule: every hour"
    echo "Action: $(echo "$TEXT" | sed 's/every.*hour//g' | xargs)"
elif echo "$TEXT" | grep -qi "every.*morning"; then
    echo "Schedule: daily at 8am (cron: 0 8 * * *)"
    echo "Action: $(echo "$TEXT" | sed 's/every.*morning//g' | xargs)"
elif echo "$TEXT" | grep -qi "every.*night"; then
    echo "Schedule: daily at 10pm (cron: 0 22 * * *)"
    echo "Action: $(echo "$TEXT" | sed 's/every.*night//g' | xargs)"
elif echo "$TEXT" | grep -qi "at.*am\|at.*pm"; then
    TIME=$(echo "$TEXT" | grep -oP '\d+(?:am|pm)' | head -1)
    echo "Schedule: daily at $TIME"
    echo "Action: $(echo "$TEXT" | sed 's/at.*am\|at.*pm//g' | xargs)"
else
    echo "Schedule: every hour (default)"
    echo "Action: $TEXT"
fi