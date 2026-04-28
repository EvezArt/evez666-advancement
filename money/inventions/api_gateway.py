#!/usr/bin/env python3
"""
Api Gateway - API gateway with rate limiting
"""
from datetime import datetime
import json

class Service:
    def __init__(self):
        self.name = api_gateway
        self.requests = []
        
    def handle(self, data):
        self.requests.append({'data': data, 'ts': datetime.now().isoformat()})
        return {'status': 'ok', 'service': self.name}

if __name__ == "__main__":
    s = Service()
    print(json.dumps(s.handle('test'), indent=2))
