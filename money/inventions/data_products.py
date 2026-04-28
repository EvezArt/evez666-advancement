#!/usr/bin/env python3
"""
Data Products - Sell data/analytics
"""
from datetime import datetime
import json

PRODUCTS = {
    "market_daily": {"price": 9.99, "desc": "Daily market brief"},
    "tech_trends": {"price": 19.99, "desc": "Weekly tech analysis"},
    "ai_insights": {"price": 29.99, "desc": "Monthly AI report"},
}

class DataProduct:
    def __init__(self):
        self.subscribers = []
        
    def subscribe(self, email, product):
        if product in PRODUCTS:
            self.subscribers.append({"email": email, "product": product, "ts": datetime.now().isoformat()})
            return {"status": "subscribed", "product": product}
        return {"status": "not_found"}
    
    def monthly_revenue(self):
        return sum(PRODUCTS[s["product"]]["price"] for s in self.subscribers)

if __name__ == "__main__":
    d = DataProduct()
    print(json.dumps(d.subscribe("test@test.com", "market_daily"), indent=2))
