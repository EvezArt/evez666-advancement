# OpenClaw Device Task Examples

## How it works
OpenClaw (Fly) → HTTP POST → device-router (localhost:3001) → WebSocket → A16 Termux agent

## Example: Cron job that runs `ls -la` on A16 every hour

Create a cron job in OpenClaw that calls the device-router endpoint:

```json
{
  "name": "a16-list-sdcard-hourly",
  "description": "List files on A16 SD card every hour",
  "schedule": { "kind": "cron", "expr": "0 * * * *" },
  "payload": {
    "kind": "systemEvent",
    "text": "A16_FILE_LIST"
  }
}
```

And a companion agent that listens for `A16_FILE_LIST` and executes the command:

```javascript
// In your OpenClaw agent logic (or a subagent):
if (message.text === 'A16_FILE_LIST') {
  await exec('curl -X POST http://localhost:3001/devices/a16/exec', {
    json: {
      type: 'shell_exec',
      payload: { cmd: 'ls -la /sdcard' }
    }
  });
}
```

## Batched example: query device health every 5 min

```bash
# One-liner to test directly from OpenClaw container
curl -X POST http://localhost:3001/devices/a16/exec \
  -H "Content-Type: application/json" \
  -d '{"type":"shell_exec","payload":{"cmd":"termux-battery-status"}}'
```

## Full round-trip flow

1. **Termux agent** on A16 connects to `ws://<fly-host>:3001` with token
2. **Heartbeats** register device in `devices` Map on router
3. **OpenClaw cron/agent** calls `POST /devices/a16/exec` with command
4. **Router** sends WS message to connected A16
5. **Agent** executes locally and returns result via WS
6. **Router** receives result, can acknowledge HTTP call (async) or store for polling

## Next: Wire this into OpenClaw's native device node system

Once the WS bridge is stable, add `a16` as a node so you can target it directly:

```javascript
await nodes.invoke({
  node: 'a16',
  invokeCommand: 'shell:ls -la /sdcard'
});
```

This requires registering `a16` in the node registry and implementing an adapter that talks to the device-router WS.
