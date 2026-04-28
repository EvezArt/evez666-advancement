#!/usr/bin/env python3
"""
Content Generator - AI content for sale
"""
from datetime import datetime
import json

CONTENT_TYPES = {
    "blog_post": {"price": 25, "words": 1000},
    "social_pack": {"price": 15, "posts": 10},
    "newsletter": {"price": 50, "words": 2000},
}

class ContentGen:
    def __init__(self):
        self.generated = []
        
    def generate(self, content_type, topic):
        if content_type in CONTENT_TYPES:
            content = {
                "type": content_type,
                "topic": topic,
                "price": CONTENT_TYPES[content_type]["price"],
                "ts": datetime.now().isoformat()
            }
            self.generated.append(content)
            return {"status": "created", "content": content}
        return {"status": "unknown_type"}
    
    def revenue(self):
        return sum(c["price"] for c in self.generated)

if __name__ == "__main__":
    c = ContentGen()
    print(json.dumps(c.generate("blog_post", "AI Automation"), indent=2))
