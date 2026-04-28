#!/usr/bin/env python3
"""
Invoice Generator - Generate invoices for clients
"""
from datetime import datetime
import json

class InvoiceGenerator:
    def __init__(self):
        self.name = "invoice_generator"
        self.transactions = []
        
    def process(self, amount, description):
        tx = {
            'amount': amount,
            'description': description,
            'ts': datetime.now().isoformat()
        }
        self.transactions.append(tx)
        return {'status': 'processed', 'tx': tx}
    
    def total(self):
        return sum(t['amount'] for t in self.transactions)

if __name__ == "__main__":
    s = InvoiceGenerator()
    print(json.dumps(s.process(29.99, 'Subscription'), indent=2))
