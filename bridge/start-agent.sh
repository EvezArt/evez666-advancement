#!/bin/bash
# Start the Termux agent as a background service

AGENT_DIR="$HOME/agent"
AGENT_FILE="termux-agent.js"
LOG_FILE="$AGENT_DIR/agent.log"
WS_URL="${1:-ws://localhost:3001}"
SECRET="${2:-my_secret_1234}"

cd "$AGENT_DIR"

# Acquire wake lock to keep CPU on
termux-wake-lock

# Start agent in background
echo "[$(date)] Starting agent..." >> "$LOG_FILE"
nohup node "$AGENT_FILE" "$WS_URL" "$SECRET" >> "$LOG_FILE" 2>&1 &
echo $! > "$AGENT_DIR/agent.pid"

echo "Agent started (PID: $(cat $AGENT_DIR/agent.pid))"
echo "Logs: tail -f $LOG_FILE"
echo "To stop: kill $(cat $AGENT_DIR/agent.pid) && termux-wake-unlock"
