#!/usr/bin/env python3
"""
API Gateway - Entry point for Distributed Economic Graph
FastAPI + Kafka producer
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import uuid
from datetime import datetime
import json
import asyncio

app = FastAPI(title="KiloClaw Economic Graph API")

# === SCHEMAS ===
class EconomicRequest(BaseModel):
    value_potential: float
    cost_budget: float
    probability: float
    metadata: Optional[Dict] = {}

class EconomicResponse(BaseModel):
    trace_id: str
    status: str
    roi_estimate: float
    path: List[str]

class HealthResponse(BaseModel):
    status: str
    kafka_connected: bool
    ledger_connected: bool

# === KAFKA PRODUCER (simulated) ===
class KafkaProducer:
    def __init__(self):
        self.connected = True
        self.topics = {}
    
    async def produce(self, topic: str, event: dict):
        if topic not in self.topics:
            self.topics[topic] = []
        self.topics[topic].append(event)
    
    def is_connected(self):
        return self.connected

# === LEDGER CLIENT (simulated) ===
class LedgerClient:
    def __init__(self):
        self.connected = True
    
    async def record(self, trace_id, node, value, cost, roi):
        return {"recorded": True}
    
    def is_connected(self):
        return self.connected

# Initialize clients
kafka = KafkaProducer()
ledger = LedgerClient()

# === ROUTES ===
@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="healthy",
        kafka_connected=kafka.is_connected(),
        ledger_connected=ledger.is_connected()
    )

@app.post("/event", response_model=EconomicResponse)
async def ingest_event(request: EconomicRequest):
    trace_id = str(uuid.uuid4())[:8]
    
    event = {
        "trace_id": trace_id,
        "timestamp": datetime.now().isoformat(),
        "payload": {
            "value_potential": request.value_potential,
            "cost_budget": request.cost_budget,
            "probability": request.probability
        },
        "metadata": request.metadata
    }
    
    # Produce to Kafka
    await kafka.produce("graph.intake", event)
    
    # Estimate ROI
    est_value = request.value_potential * request.probability
    est_cost = request.cost_budget
    roi_estimate = est_value / max(est_cost, 1)
    
    return EconomicResponse(
        trace_id=trace_id,
        status="queued",
        roi_estimate=roi_estimate,
        path=["intake"]
    )

@app.get("/event/{trace_id}")
async def get_event(trace_id: str):
    return {"trace_id": trace_id, "status": "processing", "path": ["intake", "router"]}

@app.get("/metrics")
async def get_metrics():
    return {
        "system": {
            "roi": 12.5,
            "total_value": 8940,
            "total_cost": 716
        },
        "agents": {
            "intake": {"processed": 10, "replicas": 3},
            "router": {"processed": 10, "replicas": 3},
            "sales": {"processed": 8, "replicas": 5},
            "marketing": {"processed": 4, "replicas": 2},
            "negotiator": {"processed": 6, "replicas": 3},
            "converter": {"processed": 5, "replicas": 3}
        }
    }

@app.get("/graph")
async def get_graph():
    return {
        "nodes": [
            {"id": "intake", "role": "intake", "min_roi": 0.5},
            {"id": "router", "role": "router", "min_roi": 1.0},
            {"id": "sales", "role": "sales", "min_roi": 1.5},
            {"id": "marketing", "role": "marketing", "min_roi": 1.2},
            {"id": "negotiator", "role": "negotiator", "min_roi": 2.0},
            {"id": "converter", "role": "converter", "min_roi": 2.5},
            {"id": "ledger", "role": "ledger", "min_roi": 0.1}
        ],
        "edges": [
            {"from": "intake", "to": "router"},
            {"from": "router", "to": "sales"},
            {"from": "router", "to": "marketing"},
            {"from": "sales", "to": "negotiator"},
            {"from": "sales", "to": "ledger"},
            {"from": "marketing", "to": "sales"},
            {"from": "marketing", "to": "ledger"},
            {"from": "negotiator", "to": "converter"},
            {"from": "negotiator", "to": "ledger"},
            {"from": "converter", "to": "ledger"}
        ]
    }

# === MAIN ===
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)