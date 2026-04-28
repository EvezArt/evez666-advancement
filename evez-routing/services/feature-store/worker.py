# Feature Store - Streaming feature computation
import redis
import json
import time

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def update_features(event):
    """Update rolling features per model"""
    model = event.get("model", "unknown")
    latency = event.get("latency_ms", 0)
    success = event.get("success", True)
    
    # Rolling latency
    r.hincrby("model_latency_sum", model, int(latency))
    r.hincrby("model_calls", model, 1)
    
    # Rolling success
    if success:
        r.hincrby("model_successes", model, 1)
    
    return {"model": model, "calls": r.hget("model_calls", model)}

def get_features(model: str):
    """Get computed features for model"""
    calls = int(r.hget("model_calls", model) or 0)
    latency_sum = int(r.hget("model_latency_sum", model) or 0)
    successes = int(r.hget("model_successes", model) or 0)
    
    return {
        "avg_latency": latency_sum / calls if calls > 0 else 1000,
        "success_rate": successes / calls if calls > 0 else 0.5,
        "calls": calls
    }

if __name__ == "__main__":
    print("=== FEATURE STORE RUNNING ===")
    while True:
        # Process pending telemetry
        event = r.rpop("telemetry_stream")
        if event:
            update_features(json.loads(event))
        time.sleep(0.1)