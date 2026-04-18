#!/bin/bash
# Continuous Factory with GitHub Auto-Push
# Runs factory cycle and pushes to GitHub every cycle

cd /root/.openclaw/workspace

echo "=== EVEZ666 FACTORY WITH AUTO-PUSH ==="
echo "Repos: 13 EvezArt repositories"
echo "Push: https://github.com/EvezArt/evez666-advancement"
echo ""

while true; do
    echo "[$(date +%H:%M:%S)] === FACTORY CYCLE ==="
    
    # Run factory
    python3 factory/continuous_factory.py 2>&1 | tail -5
    
    # Push changes
    git add -A 2>/dev/null
    git commit -m "Factory cycle $(date +%Y%m%d-%H%M%S) - $(date)" 2>/dev/null
    git push https://${GITHUB_TOKEN}@github.com/EvezArt/evez666-advancement.git master 2>&1 | tail -2
    
    echo "[$(date +%H:%M:%S)] ✅ Cycle complete, pushed to GitHub"
    echo "---"
    sleep 54
done