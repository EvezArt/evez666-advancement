#!/usr/bin/env python3
"""
Router Agent - ROI-based graph routing service
Decides which agent handles next based on expected ROI
"""

import os
import json
import asyncio
import random
from datetime import datetime

class RouterAgent:
    def __init__(self):
        self.role = "router"
        self.min_roi = 1.0
        
        # Edge weights: probability of routing to each node
        self.edge_weights = {
            "sales": 0.7,
            "marketing": 0.3
        }
        
        # Override from env
        weights_env = os.getenv("EDGE_WEIGHTS", "")
        if weights_env:
            self.edge_weights = json.loads(weights_env)
    
    def route(self, value_potential: float, probability: float, cost_budget: float) -> str:
        """Select next node based on ROI optimization"""
        estimated_value = value_potential * probability
        
        # Calculate expected ROI for each path
        sales_cost = 75  # average
        marketing_cost = 50  # average
        
        sales_roi = estimated_value / sales_cost
        marketing_roi = estimated_value / marketing_cost
        
        # Adjust weights based on ROI
        if sales_roi > marketing_roi * 2:
            self.edge_weights["sales"] = min(0.95, self.edge_weights["sales"] + 0.1)
            self.edge_weights["marketing"] = max(0.05, self.edge_weights["marketing"] - 0.1)
        
        # Weighted random selection
        nodes = list(self.edge_weights.keys())
        weights = list(self.edge_weights.values())
        selected = random.choices(nodes, weights=weights)[0]
        
        return selected
    
    async def process(self, event: dict) -> dict:
        """Route incoming event to appropriate agent"""
        payload = event.get("payload", {})
        value = payload.get("value_potential", 1000)
        prob = payload.get("probability", 0.5)
        cost = payload.get("cost_budget", 200)
        
        next_node = self.route(value, prob, cost)
        
        # Update event for next node
        event["node"] = next_node
        event["route_decision"] = {
            "from": "router",
            "to": next_node,
            "weights": self.edge_weights,
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "decision": "route",
            "next_node": next_node,
            "event": event,
            "weights_snapshot": self.edge_weights.copy()
        }

# === CONSUMER LOOP ===
async def consume():
    router = RouterAgent()
    print(f"Router Agent started - weights: {router.edge_weights}")
    
    while True:
        await asyncio.sleep(2)
        
        # Simulate incoming from intake
        event = {
            "trace_id": f"trace_{random.randint(1000,9999)}",
            "node": "router",
            "payload": {
                "value_potential": random.randint(500, 2500),
                "probability": random.uniform(0.3, 0.8),
                "cost_budget": random.randint(100, 500)
            },
            "timestamp": datetime.now().isoformat()
        }
        
        result = await router.process(event)
        print(f"Routed {event['trace_id']} → {result['next_node']} (weights: {result['weights_snapshot']})")

if __name__ == "__main__":
    asyncio.run(consume())