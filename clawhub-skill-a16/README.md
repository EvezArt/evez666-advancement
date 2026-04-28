# cliffy-a16-skill

A minimal clawhub skill for controlling an Android A16 device via a Termux WebSocket bridge.

## Setup

1. **Install Bun** (already done on KiloClaw):
   ```bash
   curl -fsSL https://bun.sh/install | bash
   export PATH="$HOME/.bun/bin:$PATH"
   ```

2. **Initialize and publish** from inside the skill directory:
   ```bash
   cd cliffy-a16-skill
   bunx @clawhub/cli login          # if required
   bunx @clawhub/cli publish
   ```

3. **Run the skill** once published:
   ```bash
   bunx cliffy-a16-skill ws://<fly-host>:3001 <secret> '{"type":"shell_exec","payload":{"cmd":"whoami"}}'
   ```

## Usage Examples

### Shell command
```json
{
  "type": "shell_exec",
  "payload": {
    "cmd": "ls -la /sdcard"
  }
}
```

### Read file
```json
{
  "type": "file_read",
  "payload": {
    "path": "/sdcard/Download/test.txt"
  }
}
```

### Write file
```json
{
  "type": "file_write",
  "payload": {
    "path": "/sdcard/hello.txt",
    "content": "Hello from OpenClaw"
  }
}
```

### Clipboard get/set
```json
{ "type": "get_clipboard", "payload": {} }
{ "type": "set_clipboard", "payload": { "text": "copied from OpenClaw" } }
```

### Notification
```json
{
  "type": "notify",
  "payload": {
    "title": "OpenClaw",
    "content": "Task completed",
    "priority": "high"
  }
}
```

### Screenshot
```json
{ "type": "screenshot", "payload": {} }
```

## Notes

- The Termux agent (`termux-agent.js`) must be running on the A16 device.
- Agent connects to OpenClaw's device-router WebSocket endpoint.
- Auth via `X-Device-Token` header (shared secret).
- Heartbeat every 30s keeps connection alive.
