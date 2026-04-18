#!/bin/bash
REPO="lord-evez"
cd /root/.openclaw/workspace/lord-evez

TIMESTAMP=$(date -Iseconds)
BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "none")

# Check Python syntax
SYNTAX_OK=true
for f in $(find . -name "*.py" -type f 2>/dev/null | head -5); do
    python3 -m py_compile "$f" 2>/dev/null || SYNTAX_OK=false
done

cat > /root/.openclaw/workspace/_evez/ci/quick_status_lord-evez.json << EOF
{
  "timestamp": "$TIMESTAMP",
  "repo": "lord-evez",
  "branch": "$BRANCH",
  "commit": "$COMMIT",
  "pass": $SYNTAX_OK,
  "commands": ["python3 -m py_compile"],
  "summary": "Syntax: $SYNTAX_OK"
}
EOF

echo "✓ lord-evez: $SYNTAX_OK"
