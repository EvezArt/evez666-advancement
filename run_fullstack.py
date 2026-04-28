#!/usr/bin/env python3
"""
Cron job wrapper for KiloClaw Full Stack
Runs both kiloclaw_loop.py and inference_fabric.py with rate limit handling
"""

import subprocess
import sys
import time
import json
from pathlib import Path
from datetime import datetime

WORKSPACE = Path("/root/.openclaw/workspace")
RESULTS_DIR = WORKSPACE / ".cron_results"
RESULTS_DIR.mkdir(exist_ok=True)

def run_with_retry(script_name, max_retries=1):
    """Run a script with rate limit detection and retry logic"""
    script_path = WORKSPACE / script_name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = RESULTS_DIR / f"{script_name.replace('.py','')}_{timestamp}.log"

    print(f"[{timestamp}] Starting {script_name}...")

    for attempt in range(max_retries + 1):
        if attempt > 0:
            wait_time = 30
            print(f"Rate limit detected. Waiting {wait_time}s before retry {attempt}/{max_retries}...")
            time.sleep(wait_time)

        # Run the script
        proc = subprocess.Popen(
            [sys.executable, str(script_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        # Capture output in real-time
        output_lines = []
        try:
            while True:
                line = proc.stdout.readline()
                if line:
                    output_lines.append(line)
                    print(f"  {line.rstrip()}")
                if proc.poll() is not None:
                    break

            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()

        # Check for rate limit errors
        full_output = ''.join(output_lines)
        rate_limit_detected = any([
            "rate_limit" in full_output.lower(),
            "rate limit" in full_output.lower(),
            "429" in full_output,
            "Too Many Requests" in full_output,
            "Ratelimit" in full_output
        ])

        # Save log
        with open(log_file, 'a') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"Attempt {attempt} at {datetime.now().isoformat()}\n")
            f.write(f"Return code: {proc.returncode}\n")
            f.write(f"Rate limit detected: {rate_limit_detected}\n")
            f.write(f"{'='*60}\n")
            f.write(full_output)

        if rate_limit_detected and attempt < max_retries:
            print(f"  [RETRY] Rate limit detected for {script_name}, will retry...")
            continue
        else:
            return {
                "script": script_name,
                "returncode": proc.returncode,
                "rate_limit": rate_limit_detected,
                "output": full_output,
                "log_file": str(log_file),
                "attempts": attempt + 1
            }

    # Shouldn't reach here but safety net
    return {
        "script": script_name,
        "returncode": -1,
        "rate_limit": True,
        "output": "Max retries exceeded",
        "log_file": str(log_file),
        "attempts": max_retries + 1
    }

def main():
    print("=" * 60)
    print("KILOCLAW FULL STACK - Combined System Runner")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 60)

    # Run both systems (can run in parallel since they're independent)
    print("\n[1/2] Launching KiloClaw Revenue Loop...")
    kiloclaw_result = run_with_retry("kiloclaw_loop.py")

    print("\n[2/2] Launching Inference Fabric...")
    inference_result = run_with_retry("inference_fabric.py")

    # Combined summary
    print("\n" + "=" * 60)
    print("COMBINED RESULTS")
    print("=" * 60)

    results = [kiloclaw_result, inference_result]
    combined_success = all(r["returncode"] == 0 for r in results)

    for r in results:
        status = "✅ OK" if r["returncode"] == 0 else "❌ FAILED"
        if r["rate_limit"]:
            status += " (rate limited)"
        print(f"\n{r['script']}: {status}")
        print(f"  Return code: {r['returncode']}")
        print(f"  Attempts: {r['attempts']}")
        print(f"  Log: {r['log_file']}")

    print(f"\nOverall: {'✅ ALL SYSTEMS OPERATIONAL' if combined_success else '❌ SOME SYSTEMS FAILED'}")
    print(f"Completed: {datetime.now().isoformat()}")
    print("=" * 60)

    # Write combined result JSON for programmatic access
    result_summary = {
        "timestamp": datetime.now().isoformat(),
        "combined_success": combined_success,
        "systems": results
    }
    summary_file = RESULTS_DIR / f"fullstack_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(summary_file, 'w') as f:
        json.dump(result_summary, f, indent=2)

    print(f"\nSummary saved to: {summary_file}")

    return 0 if combined_success else 1

if __name__ == "__main__":
    sys.exit(main())
