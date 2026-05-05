#!/bin/bash

run_with_retry() {
    local script="$1"
    local attempt=0
    local max_attempts=2
    local output=""

    while [ $attempt -lt $max_attempts ]; do
        output=$(python3 "$script" 2>&1)
        local exit_code=$?

        if [ $exit_code -eq 0 ] && ! echo "$output" | grep -i -q "rate_limit"; then
            echo "$output"
            return 0
        elif echo "$output" | grep -i -q "rate_limit" && [ $attempt -lt $((max_attempts-1)) ]; then
            sleep 30
            attempt=$((attempt+1))
        else
            echo "$output"
            return $exit_code
        fi
    done
}

run_with_retry "/root/.openclaw/workspace/kiloclaw_loop.py"
run_with_retry "/root/.openclaw/workspace/inference_fabric.py"