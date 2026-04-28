#!/usr/bin/env python3
"""
KiloCloud API - Get paid for AI calls
"""
from datetime import datetime
import json

PRICING = {"fast": 0.001, "standard": 0.005, "quality": 0.01}

class KiloCloudAPI:
    def __init__(self):
        self.calls = []
        self.revenue = 0.0
        
    def process(self, prompt, model="standard", api_key=None):
        if not api_key:
            return {"error": "API key required"}
        price = PRICING.get(model, 0.005)
        result = {"response": f"Done: {prompt[:30]}", "model": model, "price": price, "ts": datetime.now().isoformat()}
        self.calls.append(result)
        self.revenue += price
        return result
    
    def stats(self):
        return {"calls": len(self.calls), "revenue": self.revenue}

if __name__ == "__main__":
    api = KiloCloudAPI()
    print(json.dumps(api.process("test", "standard", "key123"), indent=2))
