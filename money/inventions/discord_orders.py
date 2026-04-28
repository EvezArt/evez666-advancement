#!/usr/bin/env python3
"""
KiloClaw Discord Bot - Take orders via Discord
"""
from datetime import datetime
import json

class DiscordOrders:
    def __init__(self):
        self.orders = []
        
    def handle_order(self, user, service):
        order = {"user": user, "service": service, "ts": datetime.now().isoformat()}
        self.orders.append(order)
        return {"status": "received", "order": order}
    
    def list_orders(self):
        return self.orders

if __name__ == "__main__":
    d = DiscordOrders()
    print(json.dumps(d.handle_order("user123", "auto_upwork_applier"), indent=2))
