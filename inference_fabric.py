#!/usr/bin/env python3
"""
INFERENCE FABRIC - GPU-aware model routing layer
"""

import json
from datetime import datetime
from hashlib import md5
import random

# === MODEL REGISTRY ===
MODELS = [
    {
        "model": "phi-mini",
        "capability": ["classification", "fast_tasks", "nurture"],
        "latency_ms": 80,
        "cost_per_1k": 0.0002,
        "gpu_class": "cpu",
        "quality_score": 0.62
    },
    {
        "model": "gpt-class-mid",
        "capability": ["sales_email", "summarization", "close"],
        "latency_ms": 350,
        "cost_per_1k": 0.002,
        "gpu_class": "a10g",
        "quality_score": 0.82
    },
    {
        "model": "llama-70b",
        "capability": ["reasoning", "complex_negotiation", "auto_close"],
        "latency_ms": 900,
        "cost_per_1k": 0.01,
        "gpu_class": "a100",
        "quality_score": 0.96
    }
]

# === TASK → MODEL MAPPING ===
TASK_MODEL_MAP = {
    "classification": "phi-mini",
    "nurture": "phi-mini",
    "sales_email": "gpt-class-mid",
    "close": "gpt-class-mid",
    "auto_close": "llama-70b",
    "reasoning": "llama-70b",
    "complex": "llama-70b"
}

# === GPU CLUSTER STATE ===
GPU_NODES = [
    {"node_id": "node-a100-1", "gpu_type": "A100", "utilization": 0.72, "memory_free_gb": 42, "active": ["llama-70b"]},
    {"node_id": "node-a10g-1", "gpu_type": "A10G", "utilization": 0.45, "memory_free_gb": 18, "active": ["gpt-class-mid"]},
    {"node_id": "node-t4-1", "gpu_type": "T4", "utilization": 0.30, "memory_free_gb": 12, "active": ["phi-mini"]},
]

# === ARBITRATION ENGINE ===
def select_model(task_type, constraints=None):
    """Select best model for task"""
    model_name = TASK_MODEL_MAP.get(task_type, "gpt-class-mid")
    model = next(m for m in MODELS if m["model"] == model_name)
    
    # Check constraints
    if constraints:
        max_latency = constraints.get("max_latency_ms", 9999)
        max_cost = constraints.get("max_cost_usd", 1.0)
        
        if model["latency_ms"] > max_latency:
            # Fall back to faster model
            for m in MODELS:
                if m["latency_ms"] <= max_latency and m["cost_per_1k"] <= max_cost:
                    model = m
                    break
    
    return model

def schedule(model, gpu_nodes):
    """Schedule model to GPU node"""
    eligible = [n for n in gpu_nodes if model["gpu_class"].lower() in n["gpu_type"].lower() or n["gpu_type"] == "T4"]
    if not eligible:
        eligible = gpu_nodes
    
    # Score nodes
    scored = []
    for n in eligible:
        score = (1 - n["utilization"]) * 0.4 + n["memory_free_gb"] * 0.3 + 0.3
        scored.append((n, score))
    
    return max(scored, key=lambda x: x[1])[0]

def route_inference(task_type, prompt, tenant_id="default"):
    """Main routing function"""
    model = select_model(task_type)
    node = schedule(model, GPU_NODES)
    
    return {
        "task_type": task_type,
        "model_selected": model["model"],
        "gpu_node": node["node_id"],
        "estimated_latency_ms": model["latency_ms"],
        "estimated_cost": model["cost_per_1k"],
        "quality_score": model["quality_score"],
        "tenant_id": tenant_id,
        "timestamp": datetime.now().isoformat()
    }

# === EXECUTE ===
def run_inference(route_result, prompt):
    """Simulate inference execution"""
    # Would actually call vLLM/TGI here
    return {
        "status": "complete",
        "model": route_result["model_selected"],
        "output": f"[Simulated {route_result['model_selected']} response to: {prompt[:50]}...]",
        "latency_ms": route_result["estimated_latency_ms"],
        "cost": route_result["estimated_cost"]
    }

# === MAIN ===
if __name__ == "__main__":
    print("=== INFERENCE FABRIC ===")
    
    tasks = [
        ("classification", "Is this a high-intent lead?"),
        ("sales_email", "Write a closing email for..."),
        ("auto_close", "Handle this urgent negotiation..."),
    ]
    
    for task_type, prompt in tasks:
        route = route_inference(task_type, prompt)
        result = run_inference(route, prompt)
        
        print(f"\n{task_type.upper()}:")
        print(f"  Model: {route['model_selected']}")
        print(f"  GPU: {route['gpu_node']}")
        print(f"  Cost: ${route['estimated_cost']:.4f}/1k")
        print(f"  Latency: {route['estimated_latency_ms']}ms")
    
    print("\n=== FABRIC READY ===")