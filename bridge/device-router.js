#!/usr/bin/env node
/**
 * OpenClaw Device Router — Fly side
 *
 * Manages WebSocket connections from mobile devices (A16 Termux agent)
 * and routes commands from OpenClaw tasks to the appropriate device.
 *
 * Run: node device-router.js
 * Requires: npm install ws express (already in bridge/node_modules)
 */

const WebSocket = require('ws');
const express = require('express');
const http = require('http');

const PORT = process.env.PORT || 3010;
const SHARED_SECRET = process.env.DEVICE_SECRET || 'my_secret_1234';

const app = express();
app.use(express.json());

// In-memory device registry (deviceId -> { ws, lastHeartbeat, stats })
const devices = new Map();

// ─── Shared HTTP server (for both Express and WS upgrades) ───────────

const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

wss.on('connection', (ws, req) => {
  const deviceToken = req.headers['x-device-token'];
  const deviceName = req.headers['x-device-name'] || 'unknown';

  if (deviceToken !== SHARED_SECRET) {
    console.log('[router] Rejected: bad token');
    ws.close(1008, 'Unauthorized');
    return;
  }

  let deviceId = null;

  ws.on('message', (data) => {
    try {
      const msg = JSON.parse(data);

      if (msg.type === 'heartbeat') {
        deviceId = msg.deviceId || deviceName;
        devices.set(deviceId, {
          ws,
          lastHeartbeat: Date.now(),
          stats: msg.stats || {},
        });
        console.log(`[router] Heartbeat from ${deviceId}`);
      }

      if (msg.type === 'command_result') {
        console.log(`[router] Result from ${msg.id}:`, msg.error ? 'ERR' : 'OK');
      }

    } catch (e) {
      console.error('[router] Parse error:', e.message);
    }
  });

  ws.on('close', () => {
    if (deviceId) {
      console.log(`[router] Device ${deviceId} disconnected`);
      devices.delete(deviceId);
    }
  });

  ws.on('error', (err) => {
    console.error('[router] WS error:', err.message);
  });
});

// ─── HTTP API ───────────────────────────────────────────────────────

// List connected devices
app.get('/devices', (req, res) => {
  const list = [];
  for (const [id, info] of devices) {
    list.push({
      id,
      connected: info.ws.readyState === WebSocket.OPEN,
      lastHeartbeat: info.lastHeartbeat,
      stats: info.stats,
    });
  }
  res.json({ devices: list });
});

// Send command to specific device
app.post('/devices/:id/exec', (req, res) => {
  const deviceId = req.params.id;
  const { type, payload } = req.body;

  const device = devices.get(deviceId);
  if (!device || device.ws.readyState !== WebSocket.OPEN) {
    return res.status(404).json({ error: 'Device not connected' });
  }

  const commandId = `cmd_${Date.now()}`;
  device.ws.send(JSON.stringify({
    type: 'command',
    id: commandId,
    type: type,
    payload,
  }));

  res.json({ status: 'sent', commandId });
});

// Reserved for admin tools
app.post('/devices/register', (req, res) => {
  res.json({ ok: true });
});

// ─── Start server ────────────────────────────────────────────────────

server.listen(PORT, () => {
  console.log(`[router] HTTP+WS on :${PORT}`);
});

// Cleanup stale devices every 45s
setInterval(() => {
  const now = Date.now();
  const staleMs = 60 * 1000;
  for (const [id, info] of devices) {
    if (now - info.lastHeartbeat > staleMs) {
      console.log(`[router] Evicting stale device ${id}`);
      devices.delete(id);
    }
  }
}, 45 * 1000);
