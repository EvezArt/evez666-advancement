#!/usr/bin/env python3
"""
KiloClaw Marketplace - Sell services 24/7
"""
from datetime import datetime
import json

SERVICES = {
    "auto_upwork_applier": {"price": 29.99, "desc": "Auto-apply to jobs", "sales": 0},
    "market_scanner": {"price": 19.99, "desc": "Market data", "sales": 0},
    "kilocloud_api": {"price": 0.001, "desc": "AI per call", "sales": 0},
    "ai_insider": {"price": 9.99, "desc": "Newsletter", "sales": 0},
}

class Marketplace:
    def __init__(self):
        self.sales = []
        
    def list_services(self):
        return [{"id": k, **v} for k, v in SERVICES.items()]
    
    def purchase(self, service_id, email):
        if service_id in SERVICES:
            sale = {"service": service_id, "email": email, "price": SERVICES[service_id]["price"], "ts": datetime.now().isoformat()}
            self.sales.append(sale)
            SERVICES[service_id]["sales"] += 1
            return {"status": "success", "sale": sale}
        return {"status": "not_found"}
    
    def revenue(self):
        return sum(s["price"] for s in self.sales)

if __name__ == "__main__":
    m = Marketplace()
    print(json.dumps(m.list_services(), indent=2))
