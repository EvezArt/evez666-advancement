#!/bin/bash
# Brief Once - Save context that persists forever
# Usage: brief_once "key insight or context to remember"

CONTENT="$1"
BRIEF_FILE="/root/.openclaw/workspace/memory/brief_once.md"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

if [ -z "$CONTENT" ]; then
    echo "Usage: brief_once <message to remember>"
    echo "Example: brief_once 'Steven prefers brief responses, no corporate speak'"
    exit 1
fi

# Create the brief file if it doesn't exist
mkdir -p "$(dirname "$BRIEF_FILE")"

# Append to brief memory
echo "" >> "$BRIEF_FILE"
echo "## $TIMESTAMP" >> "$BRIEF_FILE"
echo "$CONTENT" >> "$BRIEF_FILE"

echo "✓ Saved to brief memory: $CONTENT"

# Also save to Mem0 if available
if command -v mcporter &> /dev/null; then
    echo "Attempting Mem0 sync..."
    # This would call Mem0 API to store the memory
fi