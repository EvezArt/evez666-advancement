#!/usr/bin/env python3
"""
Natural Language Scheduler - EVEZ
Parses natural language into cron jobs and scheduled tasks.
"""

import re
import sys
import json
import subprocess
from datetime import datetime

# Time patterns
TIME_PATTERNS = {
    # Every X units
    r'every\s+(\d+)\s*(minute|minutes|min|m)': lambda m: ('interval', int(m.group(1)) * 60 * 1000),
    r'every\s+(\d+)\s*(hour|hours|hr|h)': lambda m: ('interval', int(m.group(1)) * 60 * 60 * 1000),
    r'every\s+(\d+)\s*(day|days|d)': lambda m: ('interval', int(m.group(1)) * 24 * 60 * 60 * 1000),
    r'every\s+(\d+)\s*(week|weeks|w)': lambda m: ('interval', int(m.group(1)) * 7 * 24 * 60 * 60 * 1000),
    
    # Every morning/afternoon/evening/night
    r'every\s+morning': lambda m: ('cron', '0 8 * * *'),
    r'every\s+afternoon': lambda m: ('cron', '0 14 * * *'),
    r'every\s+evening': lambda m: ('cron', '0 18 * * *'),
    r'every\s+night': lambda m: ('cron', '0 22 * * *'),
    
    # At specific times
    r'at\s+(\d{1,2})(?:am|AM)': lambda m: ('cron', f'0 {int(m.group(1))} * * *'),
    r'at\s+(\d{1,2})(?:pm|PM)': lambda m: ('cron', f'0 {(int(m.group(1)) % 12) + 12} * * *'),
    r'at\s+noon': lambda m: ('cron', '0 12 * * *'),
    r'at\s+midnight': lambda m: ('cron', '0 0 * * *'),
    
    # Daily/weekly/monthly patterns
    r'daily\s+at\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?': lambda m: parse_daily(m),
    r'every\s+day\s+at\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?': lambda m: parse_daily(m),
    r'weekly\s+on\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)': lambda m: parse_weekly(m),
    r'monthly\s+on\s+the\s+(\d{1,2})(?:st|nd|rd|th)?': lambda m: parse_monthly(m),
}

DAY_MAP = {
    'monday': 1, 'tuesday': 2, 'wednesday': 3, 'thursday': 4,
    'friday': 5, 'saturday': 6, 'sunday': 0
}

def parse_daily(m):
    hour = int(m.group(1))
    minute = int(m.group(2)) if m.group(2) else 0
    period = m.group(3)
    
    if period:
        if period.lower() == 'pm' and hour != 12:
            hour += 12
        elif period.lower() == 'am' and hour == 12:
            hour = 0
    
    return ('cron', f'{minute} {hour} * * *')

def parse_weekly(m):
    day = DAY_MAP.get(m.group(1).lower(), 1)
    return ('cron', f'0 9 * * {day}')

def parse_monthly(m):
    day = int(m.group(1))
    return ('cron', f'0 9 {day} * *')

def parse_natural_language(text):
    """Parse natural language into schedule."""
    text = text.lower().strip()
    
    for pattern, handler in TIME_PATTERNS.items():
        match = re.search(pattern, text)
        if match:
            return handler(match)
    
    # Default: every hour
    return ('interval', 60 * 60 * 1000)

def extract_action(text):
    """Extract what action to perform from the text."""
    # Remove time-related phrases
    action = re.sub(r'every\s+\w+\s*(at\s+\d+(?:am|pm)?)?', '', text, flags=re.IGNORECASE)
    action = re.sub(r'daily\s+at\s+\d+(?::\d+)?(?:\s*(?:am|pm))?', '', action, flags=re.IGNORECASE)
    action = re.sub(r'weekly\s+on\s+\w+', '', action, flags=re.IGNORECASE)
    action = re.sub(r'monthly\s+on\s+the\s+\d+(?:st|nd|rd|th)?', '', action, flags=re.IGNORECASE)
    action = re.sub(r'at\s+\d+(?:am|pm)?', '', action, flags=re.IGNORECASE)
    action = re.sub(r'every\s+\d+\s+(minute|hour|day|week)', '', action, flags=re.IGNORECASE)
    
    return action.strip() or "run specified task"

def create_cron_job(name, schedule_type, schedule_value, action):
    """Create a cron job in OpenClaw."""
    
    if schedule_type == 'cron':
        schedule = {"kind": "cron", "expr": schedule_value}
        every_ms = None
    else:  # interval
        schedule = {"kind": "every", "everyMs": schedule_value}
        every_ms = schedule_value
    
    job_config = {
        "name": name,
        "description": f"NL Scheduler: {action}",
        "enabled": True,
        "schedule": schedule,
        "payload": {
            "kind": "agentTurn",
            "message": action
        },
        "delivery": {
            "mode": "none"
        },
        "sessionTarget": "isolated",
        "wakeMode": "now"
    }
    
    # Use OpenClaw CLI to create job
    cmd = [
        "openclaw", "cron", "add",
        "--json"
    ]
    
    # For now, output what would be created
    print(json.dumps({
        "status": "would_create",
        "name": name,
        "schedule_type": schedule_type,
        "schedule_value": schedule_value,
        "action": action,
        "config": job_config
    }, indent=2))
    
    return job_config

def main():
    if len(sys.argv) < 2:
        # Interactive mode - read from stdin
        text = input("Describe the task (e.g., 'every morning at 8am check my emails'): ").strip()
    else:
        text = ' '.join(sys.argv[1:])
    
    if not text:
        print("Error: No task description provided")
        sys.exit(1)
    
    # Parse the natural language
    schedule_type, schedule_value = parse_natural_language(text)
    action = extract_action(text)
    
    # Generate a name
    safe_action = re.sub(r'[^a-z0-9]', '_', action.lower())[:30]
    name = f"nl_{safe_action}_{int(datetime.now().timestamp())}"
    
    # Create the job
    result = create_cron_job(name, schedule_type, schedule_value, action)
    
    print(f"\nParsed:")
    print(f"  Schedule type: {schedule_type}")
    print(f"  Schedule value: {schedule_value}")
    print(f"  Action: {action}")

if __name__ == "__main__":
    main()