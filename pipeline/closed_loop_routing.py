#!/usr/bin/env python3
"""
EVEZ CLOSED-LOOP ROUTING SYSTEM
5-layer self-optimizing execution control:
1. Telemetry → 2. Features → 3. Learning → 4. Routing → 5. Feedback
"""

import json
import time
import hashlib
import os
from datetime import datetime
from collections import deque
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional

STATE_DIR = "/root/.openclaw/workspace/state"
LOG_FILE = f"{STATE_DIR}/routing_loop.log"

# ======================
# LAYER 1: TELEMETRY
# ======================
@dataclass
class Telemetry:
    task_id: str
    node_id: str
    model_used: str
    latency_ms: float
    queue_time_ms: float
    token_usage: int
    success: bool
    error_type: Optional[str]
    cost: float
    timestamp: float

class TelemetryIngestion:
    """High-speed telemetry capture (hot path)"""
    
    def __init__(self, buffer_size=1000):
        self.buffer = deque(maxlen=buffer_size)
        self.stream_count = 0
        
    def emit(self, task_id: str, model: str, latency: float, 
             success: bool, cost: float, tokens: int = 0):
        """Emit telemetry - no disk, in-memory only"""
        tel = Telemetry(
            task_id=task_id,
            node_id="evez-node-1",
            model_used=model,
            latency_ms=latency,
            queue_time_ms=0,
            token_usage=tokens,
            success=success,
            error_type=None if success else "unknown",
            cost=cost,
            timestamp=time.time()
        )
        self.buffer.append(tel)
        self.stream_count += 1
        return tel

# ======================
# LAYER 2: FEATURES
# ======================
class FeatureBuilder:
    """Real-time feature computation from telemetry"""
    
    def __init__(self, window_size=100):
        self.window_size = window_size
        self.features = {}
        
    def update(self, telemetry: Telemetry):
        """Convert telemetry to features (precomputed)"""
        model = telemetry.model_used
        
        # Initialize if not exists
        if model not in self.features:
            self.features[model] = {
                "latencies": deque(maxlen=self.window_size),
                "successes": deque(maxlen=self.window_size),
                "costs": deque(maxlen=self.window_size)
            }
        
        # Add to rolling windows
        self.features[model]["latencies"].append(telemetry.latency_ms)
        self.features[model]["successes"].append(1 if telemetry.success else 0)
        self.features[model]["costs"].append(telemetry.cost)
    
    def get_features(self, model: str) -> Dict:
        """Get precomputed features for model"""
        if model not in self.features:
            return {"avg_latency": 1000, "success_rate": 0.5, "avg_cost": 0.1}
        
        f = self.features[model]
        latencies = list(f["latencies"])
        successes = list(f["successes"])
        costs = list(f["costs"])
        
        return {
            "avg_latency": sum(latencies) / len(latencies) if latencies else 1000,
            "success_rate": sum(successes) / len(successes) if successes else 0.5,
            "avg_cost": sum(costs) / len(costs) if costs else 0.1
        }

# ======================
# LAYER 3: LEARNING
# ======================
class OnlineLearning:
    """Real-time model learning (contextual bandits)"""
    
    def __init__(self):
        self.model_scores = {}
        self.learning_rate = 0.1
        self.decay = 0.95
        
    def update(self, model: str, reward: float):
        """Update model score based on reward"""
        if model not in self.model_scores:
            self.model_scores[model] = 0.5
        
        # Exponential moving average update
        self.model_scores[model] = (
            self.decay * self.model_scores[model] +
            self.learning_rate * reward
        )
    
    def get_score(self, model: str) -> float:
        """Get learned score for model"""
        return self.model_scores.get(model, 0.5)

# ======================
# LAYER 4: ROUTING
# ======================
class RoutingEngine:
    """Low-latency routing decision (<5ms target)"""
    
    def __init__(self, models: List[str]):
        self.models = models
        # Model configs
        self.config = {
            "nano": {"quality": 0.6, "latency": 200, "cost": 0.001},
            "small": {"quality": 0.75, "latency": 500, "cost": 0.003},
            "medium": {"quality": 0.85, "latency": 1000, "cost": 0.015},
            "large": {"quality": 0.95, "latency": 2000, "cost": 0.075}
        }
        
    def route(self, task_complexity: int, features: Dict, learned: Dict) -> str:
        """Make routing decision - fully in-memory, no network"""
        best_model = "nano"
        best_score = -999
        
        for model in self.models:
            cfg = self.config.get(model, {"quality": 0.5, "latency": 1000, "cost": 0.1})
            feat = features.get(model, {"avg_latency": 1000, "success_rate": 0.5})
            learn = learned.get(model, 0.5)
            
            # Scoring: quality - latency_penalty - cost_penalty + learned
            alpha, beta, gamma = 0.4, 0.3, 0.3
            score = (
                cfg["quality"] * alpha -
                (feat["avg_latency"] / 2000) * beta -
                (cfg["cost"] / 0.1) * gamma +
                learn * 0.2
            )
            
            if score > best_score:
                best_score = score
                best_model = model
        
        return best_model

# ======================
# LAYER 5: FEEDBACK
# ======================
class FeedbackLoop:
    """Self-improvement mechanism - immediate reinjection"""
    
    def __init__(self, telemetry, features, learning):
        self.telemetry = telemetry
        self.features = features
        self.learning = learning
        
    def on_task_complete(self, result: Telemetry):
        """Feed outcome back into the loop instantly"""
        # 1. Emit telemetry
        # (already done at execution time)
        
        # 2. Update features
        self.features.update(result)
        
        # 3. Update learning
        reward = self.compute_reward(result)
        self.learning.update(result.model_used, reward)
        
        # 4. Adjust routing if needed (implicit in learning)
        
    def compute_reward(self, result: Telemetry) -> float:
        """Calculate reward for learning"""
        if not result.success:
            return -1.0
        
        # Reward = success - latency_penalty - cost
        latency_penalty = result.latency_ms / 2000  # normalize
        reward = 1.0 - latency_penalty - result.cost
        
        return max(-1, min(1, reward))  # clip to [-1, 1]

# ======================
# MAIN ORCHESTRATOR
# ======================
class ClosedLoopSystem:
    """The complete self-optimizing organism"""
    
    def __init__(self):
        # Initialize all 5 layers
        self.telemetry = TelemetryIngestion()
        self.features = FeatureBuilder()
        self.learning = OnlineLearning()
        self.routing = RoutingEngine(["nano", "small", "medium", "large"])
        self.feedback = FeedbackLoop(self.telemetry, self.features, self.learning)
        
        self.task_count = 0
        
    def log(self, msg):
        with open(LOG_FILE, "a") as f:
            f.write(f"[{datetime.now().isoformat()}] {msg}\n")
    
    def execute_task(self, task_complexity: int) -> Telemetry:
        """Execute one task through the full loop"""
        self.task_count += 1
        task_id = f"task-{self.task_count}"
        
        # Step 1: Route (using current state)
        model = self.routing.route(
            task_complexity,
            {m: self.features.get_features(m) for m in self.routing.models},
            self.learning.model_scores
        )
        
        # Step 2: Execute (simulated)
        cfg = self.routing.config.get(model, {"latency": 500, "cost": 0.01})
        latency = cfg["latency"] * (0.8 + (task_complexity * 0.1))
        success = task_complexity < 4  # simple success logic
        
        # Step 3: Emit telemetry
        result = self.telemetry.emit(
            task_id=task_id,
            model=model,
            latency=latency,
            success=success,
            cost=cfg["cost"],
            tokens=task_complexity * 100
        )
        
        # Step 4: Feedback (immediate)
        self.feedback.on_task_complete(result)
        
        return result
    
    def run_cycle(self, num_tasks=5):
        """Run one cycle of tasks"""
        results = []
        for i in range(num_tasks):
            complexity = (i % 4) + 1  # 1-4
            result = self.execute_task(complexity)
            results.append(result)
            
        self.log(f"CYCLE: {len(results)} tasks, routed: {set(r.model_used for r in results)}")
        return results

if __name__ == "__main__":
    system = ClosedLoopSystem()
    system.log("=== CLOSED-LOOP ROUTING SYSTEM STARTED ===")
    
    # Run 10 cycles
    for i in range(10):
        results = system.run_cycle(5)
        
        # Show learning
        scores = system.learning.model_scores
        print(f"Cycle {i+1}: {len(results)} tasks")
        print(f"  Model scores: {dict((k, round(v,3)) for k,v in scores.items())}")
    
    print(f"\nTotal tasks: {system.task_count}")
    print(f"Telemetry events: {system.telemetry.stream_count}")