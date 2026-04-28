# Telemetry Ingestor - Hot path event capture
from fastapi import FastAPI
import redis
import json

app = FastAPI(title="EVEZ Telemetry")
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

@app.post("/telemetry")
async def ingest(event: dict):
    """Ingest telemetry event - hot path"""
    # Add to streaming buffer
    r.xadd("telemetry_stream", {"data": json.dumps(event)})
    return {"ok": True, "events": r.llen("telemetry_stream")}

@app.get("/telemetry/recent")
async def recent(n: int = 10):
    """Get recent telemetry"""
    events = r.lrange("telemetry_stream", 0, n-1)
    return {"events": [json.loads(e) for e in events]}