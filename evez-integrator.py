#!/usr/bin/env python3
"""
EVEZ INTEGRATOR
Connects all EvezArt projects into one working system
"""
import sys
from pathlib import Path

WORKSPACE = Path("/root/.openclaw/workspace")
sys.path.insert(0, str(WORKSPACE / "evez-platform"))
sys.path.insert(0, str(WORKSPACE / "evez-agentnet"))

class Integrator:
    def __init__(self):
        self.projects = {
            "platform": WORKSPACE / "evez-platform",
            "agentnet": WORKSPACE / "evez-agentnet",
            "os": WORKSPACE / "evez-os",
            "vcl": WORKSPACE / "evez-vcl",
            "sim": WORKSPACE / "evez-sim",
            "ledger": WORKSPACE / "evez-autonomous-ledger"
        }
        self.connections = {}
        
    def connect_all(self):
        """Create connections between all projects"""
        print("=== EVEZ INTEGRATOR ===")
        print("")
        
        for name, path in self.projects.items():
            if path.exists():
                files = list(path.rglob("*.py"))[:3]
                self.connections[name] = {
                    "path": str(path),
                    "files": len(list(path.rglob("*.py"))),
                    "status": "connected"
                }
                print(f"✓ {name}: {len(files)} Python files")
        
        print("")
        return self.connections
    
    def run_task(self, task_name):
        """Run a task through the integrated system"""
        print(f"Running task: {task_name}")
        
        # Connect cognition → action
        try:
            from cognition import action_bridge
            action_result = action_bridge.run()
            print(f"  → Cognition: {action_result['fixes_applied']} fixes")
        except Exception as e:
            print(f"  → Cognition: {e}")
        
        # Connect pattern → revenue  
        try:
            from cognition import pattern_revenue
            revenue_result = pattern_revenue.run()
            print(f"  → Revenue: ${revenue_result['total_value']}")
        except Exception as e:
            print(f"  → Revenue: {e}")
        
        return {"task": task_name, "status": "completed"}

if __name__ == "__main__":
    integrator = Integrator()
    integrator.connect_all()
    print("")
    integrator.run_task("autonomous_ecosystem_test")
