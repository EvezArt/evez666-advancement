#!/usr/bin/env python3
"""
Subscription Manager - Handle recurring payments
"""
from datetime import datetime, timedelta
import json

PLANS = {
    "basic": {"price": 9.99, "features": ["5 API calls/day"]},
    "pro": {"price": 29.99, "features": ["100 API calls/day", "priority"]},
    "enterprise": {"price": 99.99, "features": ["unlimited", "support"]},
}

class SubscriptionManager:
    def __init__(self):
        self.subscriptions = []
        
    def subscribe(self, email, plan):
        if plan in PLANS:
            sub = {
                "email": email,
                "plan": plan,
                "price": PLANS[plan]["price"],
                "start": datetime.now().isoformat(),
                "next_billing": (datetime.now() + timedelta(days=30)).isoformat()
            }
            self.subscriptions.append(sub)
            return {"status": "active", "subscription": sub}
        return {"status": "invalid_plan"}
    
    def monthly_revenue(self):
        return sum(PLANS[s["plan"]]["price"] for s in self.subscriptions)

if __name__ == "__main__":
    m = SubscriptionManager()
    print(json.dumps(m.subscribe("test@test.com", "pro"), indent=2))
