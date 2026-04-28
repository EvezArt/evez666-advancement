# API Gateway - Entry point for EVEZ routing system
from fastapi import FastAPI, HTTPException
import redis
import json
import uuid

app = FastAPI(title="EVEZ API Gateway")
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

@app.post("/task")
async def submit_task(task: dict):
    """Submit task to routing system"""
    task_id = str(uuid.uuid4())
    task["task_id"] = task_id
    task["timestamp"] = __import__('time').time()
    
    # Queue to Redis
    r.lpush("task_queue", json.dumps(task))
    
    return {"job_id": task_id, "status": "queued"}

@app.get("/task/{task_id}")
async def get_task(task_id: str):
    """Get task status"""
    result = r.get(f"task_result:{task_id}")
    if result:
        return json.loads(result)
    return {"status": "processing"}

@app.get("/health")
async def health():
    """Health check"""
    return {"status": "ok", "routing": "online"}