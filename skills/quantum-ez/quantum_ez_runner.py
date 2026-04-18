#!/usr/bin/env python3
"""
Quantum-Eez Parameter Sweep Engine
Systematically runs quantum algorithms with varying parameters and logs results
"""

import os
import sys
import json
import csv
import subprocess
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Paths
WORKSPACE = Path("/root/.openclaw/workspace")
EXPERIMENTS_DIR = WORKSPACE / "experiments"
EXPERIMENTS_DIR.mkdir(parents=True, exist_ok=True)

METRICS_CSV = EXPERIMENTS_DIR / "quantum_metrics.csv"
LOG_DIR = WORKSPACE / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

def log(message: str):
    """Log to both console and file"""
    timestamp = datetime.now().isoformat()
    log_line = f"[{timestamp}] {message}"
    print(log_line)
    
    log_file = LOG_DIR / f"quantum_sweep_{datetime.now().strftime('%Y-%m-%d')}.log"
    with open(log_file, "a") as f:
        f.write(log_line + "\n")

def run_command(cmd: List[str]) -> Dict:
    """Run shell command and return output"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr,
            "returncode": result.returncode
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_metrics() -> Dict:
    """Get current system metrics"""
    result = run_command(["/root/.openclaw/workspace/skills/quantum-ez/quantum_ez.sh", "metrics"])
    if result["success"]:
        try:
            return json.loads(result["output"])
        except:
            pass
    return {}

def get_algos() -> List[str]:
    """Get list of available algorithms"""
    result = run_command(["/root/.openclaw/workspace/skills/quantum-ez/quantum_ez.sh", "algo", "list"])
    if result["success"]:
        try:
            data = json.loads(result["output"])
            return data.get("algorithms", [])
        except:
            pass
    return ["grover", "qaoa", "vqe", "qft", "shors", "bell", "ghz"]

def run_algo(algo: str, params: Dict = None) -> Dict:
    """Run a specific algorithm with params"""
    cmd = ["/root/.openclaw/workspace/skills/quantum-ez/quantum_ez.sh", "algo", "run", algo]
    
    if params:
        for k, v in params.items():
            cmd.extend([f"--{k}", str(v)])
    
    result = run_command(cmd)
    
    if result["success"]:
        try:
            return json.loads(result["output"])
        except:
            pass
    
    return {"error": result.get("error", "Unknown error")}

def init_csv():
    """Initialize CSV with headers if not exists"""
    if not METRICS_CSV.exists():
        with open(METRICS_CSV, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp", "algo", "params", "qubits", "circuit_depth", 
                "runtime_ms", "success", "status", "quantum_enhanced"
            ])

def log_result(algo: str, params: Dict, result: Dict, runtime: float):
    """Log result to CSV"""
    with open(METRICS_CSV, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().isoformat(),
            algo,
            json.dumps(params),
            result.get("qubits", "N/A"),
            result.get("circuit_depth", "N/A"),
            int(runtime * 1000),
            result.get("status", "unknown") != "error",
            result.get("status", "unknown"),
            result.get("quantum_enhanced", False)
        ])

def run_parameter_sweep():
    """Run comprehensive parameter sweep"""
    log("=== Starting Quantum Parameter Sweep ===")
    
    init_csv()
    algos = get_algos()
    log(f"Available algorithms: {algos}")
    
    # Define parameter sweeps for each algorithm
    sweeps = {
        "grover": [
            {"qubits": 2}, {"qubits": 3}, {"qubits": 4}
        ],
        "qaoa": [
            {"qubits": 2}, {"qubits": 3}, {"qubits": 4}
        ],
        "vqe": [
            {"qubits": 2}, {"qubits": 3}
        ],
        "qft": [
            {"qubits": 2}, {"qubits": 4}, {"qubits": 6}, {"qubits": 8}
        ],
        "shors": [
            {"qubits": 2}, {"qubits": 3}
        ],
        "bell": [
            {"qubits": 2}, {"qubits": 3}, {"qubits": 4}
        ],
        "ghz": [
            {"qubits": 3}, {"qubits": 4}, {"qubits": 5}, {"qubits": 6}
        ],
        "supremacy": [
            {"qubits": 2}, {"qubits": 3}, {"qubits": 4}
        ]
    }
    
    results = []
    
    for algo in algos:
        if algo not in sweeps:
            continue
            
        log(f"Testing {algo}...")
        
        for params in sweeps[algo]:
            start = time.time()
            result = run_algo(algo, params)
            runtime = time.time() - start
            
            log_result(algo, params, result, runtime)
            
            results.append({
                "algo": algo,
                "params": params,
                "result": result,
                "runtime": runtime
            })
            
            log(f"  {algo} {params} -> {result.get('status', 'unknown')} ({runtime:.2f}s)")
            
            # Get metrics after each run
            metrics = get_metrics()
            log(f"  Metrics: algo_runs={metrics.get('algo_runs', 'N/A')}")
    
    log("=== Parameter Sweep Complete ===")
    return results

def generate_daily_summary():
    """Generate daily summary markdown"""
    summary_file = EXPERIMENTS_DIR / "daily_summary.md"
    
    # Read CSV and analyze
    if not METRICS_CSV.exists():
        return
    
    rows = []
    with open(METRICS_CSV, "r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    # Find best configs
    algo_stats = {}
    for row in rows:
        algo = row["algo"]
        if algo not in algo_stats:
            algo_stats[algo] = {"success": 0, "total": 0, "total_runtime": 0}
        
        algo_stats[algo]["total"] += 1
        if row["success"] == "True":
            algo_stats[algo]["success"] += 1
        algo_stats[algo]["total_runtime"] += int(row["runtime_ms"])
    
    # Build summary
    summary = f"""# Quantum Experiments Daily Summary
Generated: {datetime.now().isoformat()}

## Overall Statistics
- Total Experiments: {len(rows)}
- Successful: {sum(1 for r in rows if r['success'] == 'True')}
- Failed: {sum(1 for r in rows if r['success'] == 'False')}

## Algorithm Performance

| Algorithm | Runs | Success Rate | Avg Runtime |
|-----------|------|--------------|-------------|
"""
    
    for algo, stats in algo_stats.items():
        success_rate = (stats["success"] / stats["total"] * 100) if stats["total"] > 0 else 0
        avg_runtime = stats["total_runtime"] / stats["total"] if stats["total"] > 0 else 0
        summary += f"| {algo} | {stats['total']} | {success_rate:.0f}% | {avg_runtime:.0f}ms |\n"
    
    summary += """
## Best Configurations

"""
    # Add best configs (highest success rate with most runs)
    for algo, stats in algo_stats.items():
        if stats["success"] > 0:
            summary += f"- **{algo}**: {stats['success']}/{stats['total']} successful\n"
    
    summary += """
## Next Steps
- Review failed experiments for patterns
- Increase shots for low-confidence results
- Test on real QPU when available
"""
    
    with open(summary_file, "w") as f:
        f.write(summary)
    
    log(f"Daily summary written to {summary_file}")

def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "sweep"
    
    if action == "sweep":
        run_parameter_sweep()
    elif action == "summary":
        generate_daily_summary()
    elif action == "status":
        metrics = get_metrics()
        print(json.dumps(metrics, indent=2))
        
        # Also show CSV stats
        if METRICS_CSV.exists():
            with open(METRICS_CSV, "r") as f:
                lines = f.readlines()
            print(f"\nTotal experiments logged: {len(lines)-1}")

if __name__ == "__main__":
    main()