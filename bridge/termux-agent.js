#!/usr/bin/env node
/**
 * Termux Agent for OpenClaw Android Bridge
 * Runs on A16 inside Termux, connects back to OpenClaw Fly instance
 *
 * Setup on A16:
 *   pkg install nodejs
 *   npm install -g ws
 *   termux-set-storage   # grant storage permission
 *
 * Usage: node termux-agent.js <OPENCLAW_WS_URL> <SECRET_TOKEN>
 */

const WebSocket = require('ws');
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

const WS_URL = process.argv[2];
const SECRET = process.argv[3];

if (!WS_URL || !SECRET) {
  console.error('Usage: node termux-agent.js <ws_url> <secret_token>');
  process.exit(1);
}

const HEARTBEAT_INTERVAL = 30 * 1000;
let ws = null;
let heartbeatTimer = null;

// ─── Termux utilities ──────────────────────────────────────────────

function termuxExec(command, args = []) {
  return new Promise((resolve, reject) => {
    const full = ['termux-' + command, ...args];
    exec(full.join(' '), { maxBuffer: 10 * 1024 * 1024 }, (err, stdout, stderr) => {
      if (err) return reject(stderr || err.message);
      resolve(stdout.trim());
    });
  });
}

// Battery, WiFi, storage, uptime
async function getDeviceStats() {
  const stats = {
    battery: 'unknown',
    wifi_ssid: 'unknown',
    storage_free_mb: 0,
    uptime_seconds: 0,
  };

  try {
    // Battery (via termux-battery-status, if installed)
    const batt = await termuxExec('battery-status').catch(() => null);
    if (batt) stats.battery = batt;
  } catch (_) {}

  try {
    // WiFi SSID (termux-wifi-connectioninfo)
    const wifi = await termuxExec('wifi-connectioninfo').catch(() => null);
    if (wifi) {
      const ssidMatch = wifi.match(/ssid":"([^"]+)"/);
      if (ssidMatch) stats.wifi_ssid = ssidMatch[1];
    }
  } catch (_) {}

  try {
    // Storage (df on /data)
    const df = exec('df /data', (err, stdout) => {
      if (!err && stdout) {
        const lines = stdout.split('\n');
        const parts = lines[1]?.split(/\s+/);
        if (parts && parts[3]) {
          stats.storage_free_mb = Math.round(parseInt(parts[3], 10) / 1024);
        }
      }
    });
  } catch (_) {}

  try {
    // Uptime
    const up = fs.readFileSync('/proc/uptime', 'utf8').split(' ')[0];
    stats.uptime_seconds = Math.floor(parseFloat(up));
  } catch (_) {}

  return stats;
}

// Execute command handlers
async function handleCommand(cmd) {
  const { id, type, payload } = cmd;

  let result;
  let error = null;

  try {
    switch (type) {
      case 'shell_exec': {
        const { cmd: command, timeout = 30000 } = payload;
        result = await new Promise((resolve, reject) => {
          exec(command, { maxBuffer: 10 * 1024 * 1024, timeout }, (err, stdout, stderr) => {
            if (err) reject(stderr || err.message);
            else resolve(stdout.trim());
          });
        });
        break;
      }

      case 'file_read': {
        const { path: filepath } = payload;
        if (!fs.existsSync(filepath)) throw new Error('File not found');
        result = fs.readFileSync(filepath, 'utf8');
        break;
      }

      case 'file_write': {
        const { path: filepath, content } = payload;
        fs.writeFileSync(filepath, content, 'utf8');
        result = `Wrote ${content.length} bytes to ${filepath}`;
        break;
      }

      case 'get_clipboard': {
        result = await termuxExec('clipboard-get');
        break;
      }

      case 'set_clipboard': {
        const { text } = payload;
        await termuxExec('clipboard-set', [text]);
        result = 'Clipboard updated';
        break;
      }

      case 'notify': {
        const { title, content, priority = 'normal' } = payload;
        await termuxExec('notification', ['-t', title, '-c', content, '-p', priority]);
        result = 'Notification sent';
        break;
      }

      case 'screenshot': {
        // Requires termux-screencap (pkg install termux-api)
        const screenshotPath = '/sdcard/Pictures/openclaw_screenshot_' + Date.now() + '.png';
        await termuxExec('screencap', ['-f', screenshotPath]);
        result = { path: screenshotPath, note: 'Saved to Pictures/' };
        break;
      }

      default:
        throw new Error(`Unknown command type: ${type}`);
    }
  } catch (e) {
    error = e.message || String(e);
  }

  return { id, result, error };
}

// ─── WebSocket lifecycle ───────────────────────────────────────────

function connect() {
  ws = new WebSocket(WS_URL, {
    headers: {
      'X-Device-Token': SECRET,
      'X-Device-Name': 'a16',
    },
  });

  ws.on('open', () => {
    console.log('[agent] Connected to OpenClaw');
    // Start heartbeat
    heartbeatTimer = setInterval(async () => {
      if (ws.readyState === WebSocket.OPEN) {
        const stats = await getDeviceStats();
        ws.send(JSON.stringify({
          type: 'heartbeat',
          deviceId: 'a16',
          stats,
        }));
      }
    }, HEARTBEAT_INTERVAL);
  });

  ws.on('message', async (data) => {
    try {
      const cmd = JSON.parse(data);
      if (cmd.type !== 'command') return;

      const response = await handleCommand(cmd);
      ws.send(JSON.stringify({ ...response, type: 'command_result' }));
    } catch (e) {
      ws.send(JSON.stringify({
        type: 'command_result',
        id: 'unknown',
        error: e.message,
      }));
    }
  });

  ws.on('close', () => {
    console.log('[agent] Disconnected — reconnecting in 5s...');
    clearInterval(heartbeatTimer);
    setTimeout(connect, 5000);
  });

  ws.on('error', (err) => {
    console.error('[agent] WS error:', err.message);
  });
}

console.log('[agent] Starting Termux agent for A16...');
connect();
