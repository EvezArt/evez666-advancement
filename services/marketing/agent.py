#!/usr/bin/env python3
"""
Marketing Agent Microservice
K8s-ready agent that generates demand and modifies probability
"""

import os
import json
import asyncio
import random
from datetime import datetime
from dataclasses import dataclass

@dataclass
class MarketingEvent:
    trace_id: str
    value_potential: float
    probability: float

class MarketingAgent:
    def __init__(self):
        self.role = os.getenv("ROLE", "marketing")
        self.min_roi = float(os.getenv("MIN_ROI", "1.2"))
        self.stats = {"processed": 0, "rejected": 0, "value": 0, "cost": 0}
    
    async def process(self, event: MarketingEvent) -> dict:
        """Process marketing campaign for lead"""
        # Simulate marketing compute cost
        cost = random.uniform(20, 80)
        
        # Marketing increases probability of conversion
        prob_boost = random.uniform(0.1, 0.3)
        new_probability = min(0.95, event.probability + prob_boost)
        
        # ROI calculation
        roi = (event.value_potential * new_probability) / cost
        
        if roi < self.min_roi:
            self.stats["rejected"] += 1
            return {"decision": "drop", "roi": roi}
        
        self.stats["processed"] += 1
        self.stats["cost"] += cost
        self.stats["value"] += event.value_potential * new_probability
        
        # Output probability boost for next agent
        return {
            "decision": "route",
            "roi": roi,
            "next_node": "sales",
            "probability_boost": prob_boost,
            "campaign_id": f"camp_{random.randint(1000,9999)}"
        }

# === KAFKA CONSUMER ===
async def consume_and_process():
    agent = MarketingAgent()
    
    # In production: kafka.consumer("graph.marketing")
    print(f"Marketing Agent started - min_roi: {agent.min_roi}")
    
    while True:
        # Simulate incoming events
        await asyncio.sleep(1)
        
        event = MarketingEvent(
            trace_id=f"trace_{random.randint(1000,9999)}",
            value_potential=random.randint(500, 2000),
            probability=random.uniform(0.3, 0.7)
        )
        
        result = await agent.process(event)
        
        print(f"Processed {event.trace_id}: {result['decision']} (ROI: {result.get('roi', 0):.1f})")

if __name__ == "__main__":
    asyncio.run(consume_and_process())