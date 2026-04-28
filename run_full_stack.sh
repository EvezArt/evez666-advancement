#!/bin/bash

# Function to run a script with retry on rate_limit
run_with_retry() {
    local script="$1"
    local output
    if output=$(python3 "$script" 2>&1); then
        echo "$output"
        return 0
    else
        # Check if the error contains rate_limit (case insensitive)
        if echo "$output" | grep -i -q "rate_limit"; then
            echo "Rate limit detected, waiting 30s and retrying..."
            sleep 30
            if output=$(python3 "$script" 2>&1); then
                echo "$output"
                return 0
            else
                echo "Failed after retry: $output"
                return 1
            fi
        else
            echo "$output"
            return 1
        fi
    fi
}

echo "=== Running kiloclaw_loop.py ==="
run_with_retry "/root/.openclaw/workspace/kiloclaw_loop.py"
echo
echo "=== Running inference_fabric.py ==="
run_with_retry "/root/.openclaw/workspace/inference_fabric.py"