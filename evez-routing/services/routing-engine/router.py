# Routing Engine - In-memory decision core
import redis
import json

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Model configs
MODELS = {
    "nano": {"quality": 0.6, "latency": 200, "cost": 0.001},
    "small": {"quality": 0.75, "latency": 500, "cost": 0.003},
    "medium": {"quality": 0.85, "latency": 1000, "cost": 0.015},
    "large": {"quality": 0.95, "latency": 2000, "cost": 0.075}
}

def get_features(model: str):
    """Get features from feature store"""
    calls = int(r.hget("model_calls", model) or 0)
    latency_sum = int(r.hget("model_latency_sum", model) or 0)
    successes = int(r.hget("model_successes", model) or 0)
    
    return {
        "avg_latency": latency_sum / calls if calls > 0 else 1000,
        "success_rate": successes / calls if calls > 0 else 0.5
    }

def route(task_features: dict = None) -> str:
    """Route task to optimal model - in-memory, no network"""
    best_model = "nano"
    best_score = -999
    
    # Get learned scores
    learned = {}
    for model in MODELS:
        score = r.get(f"learned_score:{model}")
        learned[model] = float(score) if score else 0.5
    
    for model, cfg in MODELS.items():
        features = get_features(model)
        
        # Score: quality - latency_penalty - cost + learned
        score = (
            cfg["quality"] * 0.4 -
            (features["avg_latency"] / 2000) * 0.3 -
            (cfg["cost"] / 0.1) * 0.3 +
            learned.get(model, 0.5) * 0.2
        )
        
        if score > best_score:
            best_score = score
            best_model = model
    
    return best_model

if __name__ == "__main__":
    print("=== ROUTING ENGINE RUNNING ===")
    import time
    while True:
        task = r.rpop("task_queue")
        if task:
            task_data = json.loads(task)
            model = route()
            print(f"Routed task {task_data.get('task_id','?')} -> {model}")
            r.lpush(f"routed_tasks:{model}", task)
        time.sleep(0.1)