#!/usr/bin/env node
/**
 * cliffy-a16-skill
 *
 * Publishes a device command to the A16 Termux agent via WebSocket.
 * Designed for clawnet/cliffy runtime execution.
 */

const WebSocket = require('ws');

const WS_URL = process.env.WS_URL || process.argv[2];
const SECRET = process.env.SECRET || process.argv[3];

if (!WS_URL || !SECRET) {
  console.error('Usage: cliffy-a16-skill <ws_url> <secret> [command_json]');
  process.exit(1);
}

// Parse incoming command from stdin/cli
let commandPayload = null;
if (process.argv[4]) {
  try {
    commandPayload = JSON.parse(process.argv[4]);
  } catch (_) {
    commandPayload = { type: 'shell_exec', payload: { cmd: process.argv[4] } };
  }
}

// Connect and send
const ws = new WebSocket(WS_URL, {
  headers: {
    'X-Device-Token': SECRET,
    'X-Device-Name': 'a16-cli',
  },
});

ws.on('open', () => {
  console.log('[skill] Connected to A16 agent');
  if (commandPayload) {
    ws.send(JSON.stringify(commandPayload));
  } else {
    // Interactive mode: read JSON from stdin
    let buffer = '';
    process.stdin.setEncoding('utf8');
    process.stdin.on('data', (chunk) => { buffer += chunk; });
    process.stdin.on('end', () => {
      if (buffer.trim()) {
        try {
          const cmd = JSON.parse(buffer);
          ws.send(JSON.stringify(cmd));
        } catch (e) {
          console.error('Invalid JSON on stdin');
          process.exit(1);
        }
      } else {
        console.log('No command provided. Send JSON to stdin, e.g.:');
        console.log('  {"type":"shell_exec","payload":{"cmd":"whoami"}}');
        ws.close();
      }
    });
  }
});

ws.on('message', (data) => {
  const msg = JSON.parse(data);
  if (msg.type === 'command_result') {
    if (msg.error) {
      console.error('[skill] ERROR:', msg.error);
      process.exit(1);
    } else {
      console.log('[skill] RESULT:', msg.result);
      process.exit(0);
    }
  }
});

ws.on('error', (err) => {
  console.error('[skill] WS error:', err.message);
  process.exit(1);
});

ws.on('close', () => {
  // Exit after close if we already got a result
});
