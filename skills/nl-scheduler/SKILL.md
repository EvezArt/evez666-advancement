# NL Scheduler Skill

**Parse natural language into cron jobs and scheduled tasks.**

## Triggers

- "every [time]" - "every morning", "every night", "every week"
- "at [time]" - "at 8am", "at noon", "at 6pm"
- "every [number] [unit]" - "every 5 minutes", "every 2 hours", "every 3 days"
- "daily at", "weekly on", "monthly on"
- "when [event]" - "when new email", "when file added"

## Parse Examples

| Natural Language | Cron Expression | Interval |
|------------------|-----------------|----------|
| every morning | 0 8 * * * | Daily 8am |
| every night at 10pm | 0 22 * * * | Daily 10pm |
| every 5 minutes | every 5min | 5 min |
| every hour | every 1hr | 1 hour |
| every day at noon | 0 12 * * * | Daily 12pm |
| every week on monday | 0 9 * * 1 | Weekly Mon 9am |
| every month on the 1st | 0 9 1 * * | Monthly 1st 9am |

## Usage

```bash
# Create a scheduled task from natural language
nl-scheduler create "every morning at 8am check my emails and summarize them"

# List scheduled tasks
nl-scheduler list

# Delete a task
nl-scheduler delete <task-id>
```

## Output

Creates cron jobs in OpenClaw with:
- Natural language description
- Parsed schedule
- Auto-generated name
- delivery.mode = "none" (silent)