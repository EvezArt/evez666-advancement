#!/usr/bin/env python3
"""
Invoice System - Generate and send invoices
"""
from datetime import datetime
import json

class InvoiceSystem:
    def __init__(self):
        self.invoices = []
        
    def create_invoice(self, client, items):
        """Create invoice"""
        total = sum(i["price"] * i["qty"] for i in items)
        invoice = {
            "id": f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "client": client,
            "items": items,
            "total": total,
            "status": "pending",
            "created": datetime.now().isoformat()
        }
        self.invoices.append(invoice)
        return invoice
    
    def send_via_email(self, invoice_id):
        """Send invoice via Composio Gmail"""
        # Would call composio.GMAIL_SEND_EMAIL
        return {"status": "sent", "invoice": invoice_id}

if __name__ == "__main__":
    inv = InvoiceSystem()
    print(json.dumps(inv.create_invoice("Client A", [{"desc": "API Service", "price": 50, "qty": 1}]), indent=2))
