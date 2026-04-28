#!/bin/bash
# Run cognition-action bridge every 15 minutes
/usr/bin/python3 /root/.openclaw/workspace/evez-agentnet/cognition/action_bridge.py >> /root/.openclaw/workspace/factory/bridge_log.txt 2>&1
