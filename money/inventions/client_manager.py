#!/usr/bin/env python3
"""
Client Manager - Track clients and invoices
"""
from datetime import datetime
import json

class ClientManager:
    def __init__(self):
        self.clients = []
        
    def add_client(self, name, email, plan):
        client = {{
            'name': name,
            'email': email,
            'plan': plan,
            'since': datetime.now().isoformat()
        }}
        self.clients.append(client)
        return client
    
    def list_clients(self):
        return self.clients

if __name__ == "__main__":
    m = ClientManager()
    print(json.dumps(m.add_client('Acme Corp', 'billing@acme.com', 'pro'), indent=2))
