# Health Monitor Skill

**Monitor EVEZ systems and alert when things break.**

## What It Checks

- EVEZ services: localhost:4040, localhost:4041, localhost:3847
- Cron job statuses (consecutiveErrors)
- API rate limits
- Memory/disk usage
- Network connectivity

## Usage

```
health-monitor check        # Run full health check
health-monitor services     # Check EVEZ services only
health-monitor crons        # Check cron job health
health-monitor alert        # Create alert if critical
```

## Alert Levels

- 🟢 **OK** - Everything healthy
- 🟡 **WARNING** - Minor issues (rate limits)
- 🔴 **CRITICAL** - Systems down

## Cron Integration

Runs automatically:
- Every 15 minutes via health-check cron
- On cron failure, auto-Route Failover slows down

## Output

Creates /root/.openclaw/workspace/monitoring/health.json with:
- timestamp
- status level
- services checked
- issues found