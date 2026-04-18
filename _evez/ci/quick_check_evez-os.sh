#!/bin/bash
# EVEZ Quick Check - evez-os
REPO="evez-os"
cd /root/.openclaw/workspace/evez-os

echo "=== EVEZ QUICK CHECK: $REPO ==="
TIMESTAMP=$(date -Iseconds)
BRANCH=$(git branch --show-current)
COMMIT=$(git rev-parse --short HEAD)

# Check for quick test
HAS_TESTS=false
if [ -d "tests" ] || ls *test*.py 2>/dev/null | grep -q .; then
    HAS_TESTS=true
fi

# Simple syntax check on Python files
SYNTAX_OK=true
for f in $(find . -name "*.py" -type f | head -5); do
    python3 -m py_compile "$f" 2>/dev/null || SYNTAX_OK=false
done

# Write status
cat > /root/.openclaw/workspace/_evez/ci/quick_status_evez-os.json << EOF
{
  "timestamp": "$TIMESTAMP",
  "repo": "evez-os",
  "branch": "$BRANCH",
  "commit": "$COMMIT",
  "pass": $SYNTAX_OK,
  "has_tests": $HAS_TESTS,
  "commands": ["python3 -m py_compile *.py"],
  "summary": "Syntax check $SYNTAX_OK, tests: $HAS_TESTS"
}
EOF

echo "Status: $SYNTAX_OK"
echo "Branch: $BRANCH"
echo "Commit: $COMMIT"