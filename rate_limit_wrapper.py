#!/usr/bin/env python3
"""
Rate-limited job wrapper — use at the top of any cron-triggered script.
Checks provider quotas, applies backoff, and logs decisions to heartbeat-state.json.

Usage:
  python3 rate_limit_wrapper.py --job FullStack --provider github_models,exa -- /path/to/real_job.py [args...]
  python3 rate_limit_wrapper.py --job MoneyMachine --provider github_models --bash "./money_machine.py"
"""
import sys, os, json, subprocess, argparse, time
from pathlib import Path

RATE_LIMIT_DEFENSE = Path("/root/.openclaw/workspace/rate_limit_defense.py")
HEARTBEAT_STATE = Path("/root/.openclaw/workspace/heartbeat-state.json")

def load_heartbeat() -> dict:
    if HEARTBEAT_STATE.exists():
        with open(HEARTBEAT_STATE) as f:
            return json.load(f)
    return {}

def save_heartbeat(data: dict):
    with open(HEARTBEAT_STATE, "w") as f:
        json.dump(data, f, indent=2)

def record_rate_limit_check(job_name: str, providers: list, allowed: bool, backoff: int = 0):
    hb = load_heartbeat()
    # ensure rate_limits section exists
    hb.setdefault("rate_limits", {})
    hb["rate_limits"][job_name] = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "providers": providers,
        "allowed": allowed,
        "backoff_seconds": backoff,
    }
    save_heartbeat(hb)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--job", required=True, help="Job name (for logging)")
    parser.add_argument("--provider", required=False, help="Comma-separated provider names")
    parser.add_argument("cmd", nargs="+", help="Command to run (including args)")
    args = parser.parse_args()

    providers = [p.strip() for p in (args.provider or "").split(",") if p.strip()]
    
    # Check rate limits before proceeding
    if providers:
        # Import the defense module dynamically
        sys.path.insert(0, str(RATE_LIMIT_DEFENSE.parent))
        from rate_limit_defense import _manager
        
        denied = False
        backoff_reasons = []
        for prov in providers:
            allowed, backoff = _manager.consume(prov)
            if not allowed:
                denied = True
                backoff_reasons.append(f"{prov}:{backoff}s")
        
        record_rate_limit_check(args.job, providers, allowed=not denied, 
                               backoff=int(max([int(b.split(':')[1]) for b in backoff_reasons], default=0)))
        
        if denied:
            print(f"⏸️  {args.job} rate-limited → backoff: {', '.join(backoff_reasons)}")
            sys.exit(1)  # exit with error to signal skip
    
    # Execute the real command
    cmd = args.cmd
    print(f"▶️  {args.job}: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False)
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
