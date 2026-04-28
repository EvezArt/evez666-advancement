#!/bin/bash
# Termux setup script for A16 Android bridge
# Run this inside Termux on your Samsung A16

set -e

echo "=== Termux A16 Bridge Installer ==="

# Update packages
pkg update -y && pkg upgrade -y

# Install Node.js and dependencies
pkg install -y nodejs

# Install WebSocket client library globally
npm install -g ws

# Grant storage permission (required for screenshots/file access)
termux-set-storage

# Create directory for agent
mkdir -p $HOME/agent
cd $HOME/agent

# Fetch agent from your Fly instance (adjust URL to match your deployment)
# Option 1: Use wget/curl if you have the file hosted
# wget https://your-fly-app.com/bridge/termux-agent.js

# Option 2: You can also paste the agent code directly into a file
# nano termux-agent.js

echo "=== Installation complete ==="
echo ""
echo "Next steps:"
echo "1. Place termux-agent.js in $HOME/agent"
echo "2. Run:"
echo "   node termux-agent.js ws://<your-fly-host>:3001 <shared-secret>"
echo ""
echo "Or use the provided launch script:"
echo "   ./start-agent.sh"
echo ""
echo "To run in background persistently:"
echo "   termux-wake-lock"
echo "   nohup node termux-agent.js ... > agent.log 2>&1 &"
