#!/usr/bin/env python3
"""
EVEZ-OMNI CONTINUOUS MONITOR
============================
Simply keeps EVEZ-OMNI running and evolving - no complex training loss
"""

import numpy as np
import time
import json
import sys
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, '/root/.openclaw/workspace/ml')
from evez_omni_v2 import OmniV2Engine

LOG_FILE = Path("/root/.openclaw/workspace/ml/monitor_log.json")
LOG_FILE.parent.mkdir(exist_ok=True)

class EvezMonitor:
    """Simply keeps EVEZ-OMNI processing and evolving"""
    
    def __init__(self):
        print("🚀 Starting EVEZ-OMNI Monitor...")
        self.engine = OmniV2Engine()
        self.step = 0
        self.history = []
        
    def random_inputs(self) -> Dict:
        """Generate random valid inputs"""
        return {
            "physics_params": {},
            "evolve_lattice": np.random.rand() > 0.3,
            "decision": {
                "actions": np.random.choice(["analyze", "create", "optimize", "reflect"], 
                    size=np.random.randint(1, 4)).tolist(),
                "confidence": np.random.uniform(0.6, 1.0),
                "context": {"domain": np.random.choice(["code", "reason", "create", "meta"])}
            },
            "workflow": {"steps": np.random.randint(3, 12)},
            "local_data": {"samples": [{"d": i} for i in range(np.random.randint(3, 8))]},
            "task": {
                "actions": ["fetch", "compute", "store", "notify", "verify"][:np.random.randint(2, 5)],
                "dependencies": [0, 1] if np.random.rand() > 0.5 else []
            },
            "current_state": {"value": np.random.rand()},
            "neural_input": np.random.rand(512)
        }
    
    def step(self) -> Dict:
        """Process one step"""
        inputs = self.random_inputs()
        results = self.engine.process(inputs)
        
        # Simple metrics (all positive)
        metrics = {
            "step": self.step,
            "physics_uncertainty": results.get("physics", {}).get("uncertainty_product", 0),
            "metacognitive_errors": len(results.get("metacognitive", {}).get("errors_detected", [])),
            "privacy_budget": results.get("adaptive", {}).get("privacy_budget", 1.0),
            "temporal_steps": len(results.get("temporal", {}).get("orchestration", [])),
            "neural_output_magnitude": float(np.linalg.norm(results.get("neural", [0]*128))),
            "experience_buffer_size": len(self.engine.experience_buffer)
        }
        
        return metrics
    
    def run(self, steps_per_report: int = 100):
        """Run forever"""
        print(f"   Logging to: {LOG_FILE}")
        print(f"   Press Ctrl+C to stop")
        print()
        
        while True:
            try:
                # Process step
                metrics = self.step()
                self.step += 1
                self.history.append(metrics)
                
                # Keep last 10000
                if len(self.history) > 10000:
                    self.history = self.history[-10000:]
                
                # Report every 100 steps
                if self.step % steps_per_report == 0:
                    recent = self.history[-steps_per_report:]
                    
                    avg_uncertainty = np.mean([m["physics_uncertainty"] for m in recent])
                    avg_privacy = np.mean([m["privacy_budget"] for m in recent])
                    avg_neural = np.mean([m["neural_output_magnitude"] for m in recent])
                    
                    print(f"📊 [Step {self.step:05d}] "
                          f"Uncertainty: {avg_uncertainty:.2f} | "
                          f"Privacy: {avg_privacy:.3f} | "
                          f"Neural: {avg_neural:.2f} | "
                          f"XP buffer: {len(self.engine.experience_buffer)}")
                    
                    # Save log
                    with open(LOG_FILE, 'w') as f:
                        json.dump({
                            "current_step": self.step,
                            "history": self.history[-1000:]
                        }, f, indent=2)
                
                time.sleep(0.005)  # Brief pause
                
            except KeyboardInterrupt:
                print("\n🛑 Stopped")
                break
            except Exception as e:
                print(f"⚠️ {e}")
                time.sleep(1)

if __name__ == "__main__":
    monitor = EvezMonitor()
    monitor.run()