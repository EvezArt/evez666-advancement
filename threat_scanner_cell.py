#!/usr/bin/env python3
"""
Threat Scanner Cell — integrates Jigsawstack scanner signals → ontological detections.
Wraps existing evez-agentnet scanner output into CellNetwork format.
"""

import json
import time
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("threat_scanner")

SCANNER_OUTPUT = Path("/root/.openclaw/workspace/evez-agentnet/scanner/scan_results.jsonl")

def load_latest_scans(n: int = 20) -> List[Dict]:
    """Load the n most recent scanner entries."""
    if not SCANNER_OUTPUT.exists():
        return []
    with open(SCANNER_OUTPUT) as f:
        lines = f.readlines()
    results = []
    for line in lines[-n:]:
        try:
            obj = json.loads(line)
            results.append(obj)
        except: pass
    return results

def analyze_sentiment_threat(sentiment: float, title: str) -> float:
    """Heuristic: negative sentiment + threat keywords → elevated severity."""
    threat_keywords = ["leak", "breach", "exploit", "vulnerability", "attack", "malware", "ransomware", "backdoor"]
    keyword_boost = 0.0
    for kw in threat_keywords:
        if kw in title.lower():
            keyword_boost += 0.2
            break
    # Sentiment below -0.6 is concerning
    sentiment_penalty = max(0.0, -sentiment - 0.6) * 0.3
    severity = 0.2 + keyword_boost + sentiment_penalty
    return min(1.0, severity)

def run_threat_scanner_cell() -> List[Dict]:
    """Consume scanner output → CellNetwork detection entities."""
    scans = load_latest_scans(30)
    detections = []
    for item in scans:
        severity = analyze_sentiment_threat(item.get("sentiment", 0.0), item.get("title", ""))
        detection = {
            "cell_id": "cell_threat_scanner_global",
            "detection_type": "threat" if severity >= 0.6 else "generic",
            "severity": round(severity, 3),
            "confidence": 0.8,
            "signature": {
                "title": item.get("title", ""),
                "source": item.get("source", "unknown"),
                "sentiment": item.get("sentiment", 0.0),
                "url": item.get("url", ""),
                "scanned_at": item.get("scanned_at", ""),
            },
            "tags": ["threat_intel", "jigsawstack"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        detections.append(detection)
    log.info(f"Threat scanner produced {len(detections)} detections from {len(scans)} signals")
    return detections


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    detections = run_threat_scanner_cell()
    if detections:
        print("=== Threat Scanner Output ===")
        for d in detections[:5]:
            print(f"[{d['detection_type']}] sev={d['severity']:.2f} — {d['signature']['title'][:60]}")
    else:
        print("No threat detections this cycle.")
