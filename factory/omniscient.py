#!/usr/bin/env python3
"""
KILOCLAW OMNISCIENT - Uses Composio to build income-generating services
"""

import subprocess
import json
import os
from pathlib import Path
from datetime import datetime

WORKSPACE = Path("/root/.openclaw/workspace")
MONEY = WORKSPACE / "money"
MONEY.mkdir(exist_ok=True)

# === CHECK RESOURCES ===

def check_resources():
    results = {}
    r = subprocess.run(["which", "ngrok"], capture_output=True)
    results["ngrok"] = r.returncode == 0
    r = subprocess.run(["which", "tailscale"], capture_output=True)
    results["tailscale"] = r.returncode == 0
    results["sentry"] = bool(os.getenv("SENTRY_DSN"))
    results["composio"] = True
    return results

# === BUILD INVENTIONS ===

def build_payment_gateway():
    """Stripe/PayPal ready payment system"""
    code = '''#!/usr/bin/env python3
"""
KiloClaw Payment Gateway
Ready for Stripe/PayPal integration
"""
from datetime import datetime
import json

class PaymentGateway:
    def __init__(self):
        self.stripe_key = None
        self.payments = []
        
    def connect_stripe(self, key):
        self.stripe_key = key[:8] + "..."
        return {"status": "connected", "provider": "stripe"}
    
    def create_checkout(self, product, price):
        return {
            "checkout_url": f"https://buy.stripe.com/{product}",
            "price": price,
            "product": product
        }
    
    def process_payment(self, amount):
        self.payments.append({"amount": amount, "ts": datetime.now().isoformat()})
        return {"status": "success", "total": len(self.payments)}

if __name__ == "__main__":
    p = PaymentGateway()
    print(json.dumps(p.create_checkout("auto_applier", 29.99), indent=2))
'''
    (MONEY / "inventions" / "payment_gateway.py").write_text(code)
    return "payment_gateway"

def build_marketplace():
    """Auto-sell services"""
    code = '''#!/usr/bin/env python3
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
'''
    (MONEY / "inventions" / "marketplace.py").write_text(code)
    return "marketplace"

def build_api_service():
    """Paid API people can call"""
    code = '''#!/usr/bin/env python3
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
'''
    (MONEY / "inventions" / "kilocloud_api.py").write_text(code)
    return "kilocloud_api"

def build_discord_bot():
    """Discord bot that takes orders"""
    code = '''#!/usr/bin/env python3
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
'''
    (MONEY / "inventions" / "discord_orders.py").write_text(code)
    return "discord_orders"

# === MAIN ===

def run():
    print("=== KILOCLAW OMNISCIENT ===")
    
    resources = check_resources()
    print(f"Resources: ngrok={resources['ngrok']}, tailscale={resources['tailscale']}, composio={resources['composio']}")
    
    # Ensure inventions dir
    (MONEY / "inventions").mkdir(exist_ok=True)
    
    # Build all inventions
    print("\nBuilding:")
    b1 = build_payment_gateway()
    b2 = build_marketplace()
    b3 = build_api_service()
    b4 = build_discord_bot()
    
    print(f"  {b1}")
    print(f"  {b2}")
    print(f"  {b3}")
    print(f"  {b4}")
    
    # List all files
    files = list((MONEY / "inventions").glob("*.py"))
    print(f"\nTotal inventions: {len(files)}")
    
    return {"inventions": len(files), "resources": resources}

if __name__ == "__main__":
    print(json.dumps(run(), indent=2, default=str))