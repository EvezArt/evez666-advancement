#!/usr/bin/env python3
"""
image_gen - Image generation API
"""
from datetime import datetime

class Product:
    def __init__(self):
        self.name = "image_gen"
        self.desc = "Image generation API"
        
    def run(self):
        return {"product": self.name, "status": "ready", "ts": datetime.now().isoformat()}

if __name__ == "__main__":
    p = Product()
    print(p.run())
