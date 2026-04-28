#!/usr/bin/env python3
"""
Automation Services - Do work for people
"""
from datetime import datetime
import json

SERVICES = {
    "data_scrape": {"price": 50, "desc": "Web scraping"},
    "api_build": {"price": 200, "desc": "Build REST API"},
    "bot_create": {"price": 150, "desc": "Create Telegram/Discord bot"},
    "script_write": {"price": 30, "desc": "Python script"},
}

class AutoService:
    def __init__(self):
        self.orders = []
        
    def order(self, service, details):
        if service in SERVICES:
            order = {"service": service, "details": details, "price": SERVICES[service]["price"], "ts": datetime.now().isoformat()}
            self.orders.append(order)
            return {"status": "received", "order": order}
        return {"status": "not_found"}
    
    def revenue(self):
        return sum(o["price"] for o in self.orders)

if __name__ == "__main__":
    a = AutoService()
    print(json.dumps(a.order("script_write", "PDF parser"), indent=2))
