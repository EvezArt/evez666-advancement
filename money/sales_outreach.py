#!/usr/bin/env python3
"""
SALES OUTREACH - Find and contact potential customers
"""
import json
from pathlib import Path
from datetime import datetime

WORKSPACE = Path("/root/.openclaw/workspace")
PRODUCTS_DIR = WORKSPACE / "money" / "products"

# Places to find potential customers
SEARCH_QUERIES = [
    "autonomous AI agent developer",
    "LLM app developer looking for fallover",
    "quantum machine learning researcher",
    "DevOps cron automation",
    "self-healing AI system",
]

# Our value proposition
VALUE_PROPS = {
    "self_healing": "Never let rate limits kill your agent again",
    "inference_mesh": "Best model routing automatically",
    "cognition": "Your agent learns from its own errors",
    "quantum": "Ready-to-run quantum circuits",
    "cron": "14 jobs that fix themselves",
}

def find_prospects():
    """Find potential customers"""
    prospects = []
    
    # Check recent GitHub issues/PRs in our repos that might indicate needs
    # For now, return our target audience profiles
    
    print("=== SALES OUTREACH ===")
    print(f"Target audiences: {len(SEARCH_QUERIES)}")
    for q in SEARCH_QUERIES:
        print(f"  - {q}")
    
    return [
        {"audience": q, "value": VALUE_PROPS.get(q.split()[0], "EVEZ infrastructure")}
        for q in SEARCH_QUERIES
    ]

def generate_outreach_message(audience, product):
    """Generate personalized outreach"""
    templates = {
        "self_healing": "Hey, tired of rate limits killing your AI? I built auto-backoff that fixes itself.",
        "inference_mesh": "Want your LLM app to automatically use the best model? Here's how.",
        "cognition": "Your AI can learn from its mistakes. Here's the pattern detection engine.",
        "quantum": "Running quantum algorithms? Here's a library that works.",
        "cron": "14 cron jobs running autonomously with self-healing. Here's the stack.",
    }
    return templates.get(product, f"Check out this EVEZ {product} template - ${product.get('price', 29)}")

def run():
    """Execute sales outreach"""
    prospects = find_prospects()
    
    print("")
    print("Value propositions:")
    for p in prospects:
        print(f"  {p['audience']}: {p['value']}")
    
    print("")
    print("Products listed at: /money/products/buy.html")
    print("Next: Connect to actual payment to receive money")
    
    return {"audiences": len(prospects)}

if __name__ == "__main__":
    run()
