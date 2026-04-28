# A16 Android Bridge — Quick Start

## What's included

| File | Purpose |
|------|---------|
| `termux-agent.js` | Runs on A16 Termux, connects to OpenClaw WS, executes commands |
| `device-router.js` | Runs on OpenClaw Fly, manages WS connections + HTTP command API |
| `install-a16.sh` | Termux setup script (installs node, ws, permissions) |
| `start-agent.sh` | Background service launcher for Termux agent |
| `cliffy-a16-skill/` | Minimal clawhub skill for publishing + remote execution |

## Two deployment options

### Option A: Direct WebSocket bridge (fastest)
1. On OpenClaw Fly: run `node device-router.js` (keep alive)
2. On A16 Termux: run `node termux-agent.js ws://<fly-ip>:3001 <secret>`
3. Control from OpenClaw: `curl -X POST http://localhost:3001/devices/a16/exec -d '{"type":"shell_exec","payload":{"cmd":"whoami"}}'`

### Option B: Clawhub skill publish (remote execution)
1. Publish the skill: `cd cliffy-a16-skill && bunx @clawhub/cli publish`
2. Then run: `bunx cliffy-a16-skill ws://<fly-ip>:3001 <secret> '{"type":"shell_exec","payload":{"cmd":"whoami"}}'`
3. Available as a remote callable skill from any OpenClaw instance

## Commands supported

| type | payload fields | What it does |
|------|---------------|-------------|
| `shell_exec` | `cmd`, `timeout` | Run shell, get stdout |
| `file_read` | `path` | Read file contents |
| `file_write` | `path`, `content` | Write text file |
| `get_clipboard` | (none) | Get clipboard text |
| `set_clipboard` | `text` | Set clipboard |
| `notify` | `title`, `content`, `priority` | Android notification |
| `screenshot` | (none) | Screenshot → `/sdcard/Pictures/` |

## Heartbeat

Every 30s the agent sends:
```json
{
  "type": "heartbeat",
  "deviceId": "a16",
  "stats": {
    "battery": "...",
    "wifi_ssid": "...",
    "storage_free_mb": 1234,
    "uptime_seconds": 86400
  }
}
```

## Security

- Shared secret in `X-Device-Token` header
- Router evicts stale devices after 60s no heartbeat
- All communication over WS (use `wss://` in production)

---

**Status:** Terminology agent tested locally, device-router scaffolded. Ready to deploy on actual device.
