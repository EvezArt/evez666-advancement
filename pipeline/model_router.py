#!/usr/bin/env python3
"""
EVEZ DYNAMIC MODEL ROUTING
Routes requests to optimal model based on complexity, cost, confidence
"""

import json
import time
import os
from datetime import datetime

STATE_DIR = "/root/.openclaw/workspace/state"
ROUTING_LOG = f"{STATE_DIR}/model_routing.log"

# Model tier configuration
MODELS = {
    "nano": {
        "name": "gemini-2.0-flash",
        "cost_per_1k": 0.000,
        "capability": "simple_tasks",
        "latency_ms": 200
    },
    "small": {
        "name": "claude-3-haiku",
        "cost_per_1k": 0.003,
        "capability": "medium_tasks", 
        "latency_ms": 500
    },
    "medium": {
        "name": "gpt-4o-mini",
        "cost_per_1k": 0.015,
        "capability": "complex_tasks",
        "latency_ms": 1000
    },
    "large": {
        "name": "claude-3.5-sonnet",
        "cost_per_1k": 0.075,
        "capability": "reasoning",
        "latency_ms": 2000
    }
}

class ModelRouter:
    def __init__(self):
        self.state_file = f"{STATE_DIR}/routing_state.json"
        self.state = self.load_state()
        
    def load_state(self):
        if os.path.exists(self.state_file):
            with open(self.state_file) as f:
                return json.load(f)
        return {"total_requests": 0, "routing_decisions": [], "cost_savings": 0}
    
    def save_state(self):
        with open(self.state_file, "w") as f:
            json.dump(self.state, f, indent=2)
    
    def log(self, msg):
        with open(ROUTING_LOG, "a") as f:
            f.write(f"[{datetime.now().isoformat()}] {msg}\n")
    
    def analyze_complexity(self, task):
        """Estimate task complexity"""
        complexity_indicators = {
            "code": 3,
            "reasoning": 3,
            "analysis": 2,
            "summary": 1,
            "search": 1,
            "simple": 1
        }
        
        score = 1
        for indicator, weight in complexity_indicators.items():
            if indicator in task.lower():
                score = max(score, weight)
        
        # Default to simple
        return score
    
    def route(self, task, fallback_confidence_threshold=0.7):
        """Route task to optimal model"""
        self.state["total_requests"] += 1
        
        # Analyze complexity
        complexity = self.analyze_complexity(task)
        
        # Select model based on complexity
        if complexity == 1:
            model = "nano"
        elif complexity == 2:
            model = "small"
        elif complexity == 3:
            model = "medium"
        else:
            model = "large"
        
        # Cascade: if confidence low, escalate to larger model
        # (Simulated - in production would call model and check confidence)
        simulated_confidence = 0.85
        
        if simulated_confidence < fallback_confidence_threshold and model != "large":
            old_model = model
            model = MODELS.get(model, "small").get("capability", "medium_tasks")
            # Escalate
            if model == "nano":
                model = "small"
            elif model == "small":
                model = "medium"
            self.log(f"CASCADE: escalated from {old_model} to {model}")
        
        selected = MODELS[model]
        
        # Calculate cost savings (vs always using large)
        large_cost = MODELS["large"]["cost_per_1k"]
        actual_cost = selected["cost_per_1k"]
        savings = large_cost - actual_cost
        
        self.state["cost_savings"] += savings
        self.state["routing_decisions"].append({
            "task_type": task[:20],
            "model": model,
            "confidence": simulated_confidence,
            "timestamp": datetime.now().isoformat()
        })
        self.save_state()
        
        result = {
            "task": task[:30],
            "complexity": complexity,
            "routed_to": model,
            "model_name": selected["name"],
            "cost_per_1k": selected["cost_per_1k"],
            "latency_ms": selected["latency_ms"],
            "confidence": simulated_confidence,
            "savings_vs_large": savings
        }
        
        self.log(f"ROUTE: {task[:20]} -> {model} (conf={simulated_confidence})")
        return result

if __name__ == "__main__":
    router = ModelRouter()
    
    # Simulate routing various task types
    tasks = [
        "summarize this email",
        "analyze this code for bugs",
        "write a complex python algorithm",
        "simple search query",
        "debug this python code",
        "reason about this philosophical question",
        "translate this text"
    ]
    
    print("=== MODEL ROUTING DEMO ===")
    for task in tasks:
        result = router.route(task)
        print(f"Task: {result['task']}")
        print(f"  → {result['routed_to']} ({result['model_name']})")
        print(f"  Latency: {result['latency_ms']}ms, Savings: ${result['savings_vs_large']:.4f}")
        print()
    
    print(f"Total cost savings: ${router.state['cost_savings']:.4f}")