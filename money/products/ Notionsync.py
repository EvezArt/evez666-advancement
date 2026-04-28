#!/usr/bin/env python3
"""
 Notionsync - Notion to any sync
"""
from datetime import datetime

class Product:
    def __init__(self):
        self.name = " Notionsync"
        self.desc = "Notion to any sync"
        
    def run(self):
        return {"product": self.name, "status": "ready", "ts": datetime.now().isoformat()}

if __name__ == "__main__":
    p = Product()
    print(p.run())
