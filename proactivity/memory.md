# Proactive Memory - KiloClaw

## Learned Patterns & Preferences
- Mem0 integration check: Always verify MCP server availability before attempting external memory saves
- Fallback strategy: When external tools unavailable, save locally with clear documentation
- Error handling: Internal exec failures (SIGTERM) from cron subsystem checks should be handled silently unless user requests details
- State tracking: Update proactive session state immediately after completing automated tasks

## Operational Boundaries
- Do not relay internal system exec results unless explicitly requested by user
- Handle SIGTERM signals from async commands internally - they often indicate expected cleanup
- Prefer file-based fallbacks when external integrations aren't configured
- Keep proactive work quiet and non-disruptive to main session flow

## Recent Improvements
- Added structured logging for Mem0 auto-memory attempts even when tools unavailable
- Improved error resilience in cron job introspection
- Clear separation between internal system handling and user-facing communication