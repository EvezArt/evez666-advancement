#!/usr/bin/env python3
"""Analysis API - Paid service"""
import json

def analyze(data):
    return {"analysis": "completed", "price": "$0.05"}

if __name__ == "__main__":
    print(json.dumps({"service": "analysis_api", "price": 0.05}))
