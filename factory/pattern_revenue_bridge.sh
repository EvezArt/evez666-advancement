#!/bin/bash
# Run pattern-revenue bridge every hour
/usr/bin/python3 /root/.openclaw/workspace/evez-agentnet/cognition/pattern_revenue.py >> /root/.openclaw/workspace/factory/pattern_log.txt 2>&1
