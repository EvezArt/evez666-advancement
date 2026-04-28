# EVEZ Cross-Platform Workstation

## Active Integrations
- Linear (project management)
- Slack (communication)
- Discord (backup comms)
- Telegram (mobile)
- GitHub (code)
- Gmail (email)
- Google Calendar (scheduling)

## Rate Limit Strategy
- Primary: Linear → Secondary: Notion → Tertiary: Local cache
- Fallback chain defined in failover.py

## API Health Monitoring
- health_check.py runs every 5 minutes
- auto_switch.py handles failover

## Commands
- python3 health_check.py
- python3 auto_switch.py
- python3 sync_all.py
