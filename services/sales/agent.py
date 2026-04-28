#!/usr/bin/env python3
"""
Sales Agent Microservice
K8s-ready agent that converts leads to deals
"""

import os
import json
import asyncio
import random
from datetime import datetime
from dataclasses import dataclass

@dataclass
class SalesEvent:
    trace_id: str
    value_potential: float
    probability: float
    probability_boost: float = 0

class SalesAgent:
    def __init__(self):
        self.role = os.getenv("ROLE", "sales")
        self.min_roi = float(os.getenv("MIN_ROI", "1.5"))
        self.stats = {"processed": 0, "rejected": 0, "value": 0, "cost": 0}
    
    async def process(self, event: SalesEvent) -> dict:
        """Process sales outreach"""
        cost = random.uniform(30, 120)
        
        # Sales increases probability further
        sales_boost = random.uniform(0.1, 0.25)
        total_prob = min(0.95, event.probability + event.probability_boost + sales_boost)
        
        roi = (event.value_potential * total_prob) / cost
        
        if roi < self.min_roi:
            self.stats["rejected"] += 1
            return {"decision": "drop", "roi": roi}
        
        self.stats["processed"] += 1
        self.stats["cost"] += cost
        self.stats["value"] += event.value_potential * total_prob
        
        # Decision: negotiate or direct to ledger
        if total_prob > 0.7:
            return {"decision": "route", "roi": roi, "next_node": "negotiator", "deal_size": event.value_potential}
        else:
            return {"decision": "route", "roi": roi, "next_node": "ledger", "deal_size": event.value_potential}

# === KAFKA CONSUMER ===
async def consume_and_process():
    agent = SalesAgent()
    print(f"Sales Agent started - min_roi: {agent.min_roi}")
    
    while True:
        await asyncio.sleep(1)
        
        event = SalesEvent(
            trace_id=f"trace_{random.randint(1000,9999)}",
            value_potential=random.randint(500, 3000),
            probability=random.uniform(0.2, 0.6),
            probability_boost=random.uniform(0, 0.2)
        )
        
        result = await agent.process(event)
        
        print(f"Sales {event.trace_id}: {result['decision']} → {result.get('next_node')} (ROI: {result.get('roi', 0):.1f})")

if __name__ == "__main__":
    asyncio.run(consume_and_process())