#!/usr/bin/env python3
"""
CellNetwork Stream — NDJSON event feed for dashboard / external consumption.
Combines: detections, correlations, cell registry, heartbeat.
"""

import json
import time
import logging
from pathlib import Path
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("cellnetwork.stream")

STREAM_PATH = Path("/root/.openclaw/workspace/memory/cellnetwork_stream.jsonl")
ONTOLOGY_PATH = Path("/root/.openclaw/workspace/memory/ontology/graph.jsonl")
ALERT_PATH = Path("/root/.openclaw/workspace/memory/cellnetwork_alerts.jsonl")

def tail_ontology(limit: int = 50) -> List[Dict]:
    """Emit recent Detection entities."""
    if not ONTOLOGY_PATH.exists():
        return []
    with open(ONTOLOGY_PATH) as f:
        lines = f.readlines()
    events = []
    for line in lines[-limit:]:
        try:
            obj = json.loads(line)
            if obj.get("op") == "create" and obj.get("entity",{}).get("type") == "Detection":
                events.append({"type":"detection","payload":obj["entity"],"ts":obj["entity"]["properties"]["timestamp"]})
        except: pass
    return events

def tail_alerts(limit: int = 20) -> List[Dict]:
    if not ALERT_PATH.exists():
        return []
    with open(ALERT_PATH) as f:
        lines = f.readlines()
    events = []
    for line in lines[-limit:]:
        try:
            obj = json.loads(line)
            events.append({"type":"alert","payload":obj.get("alert",{}),"ts":obj.get("ts","")})
        except: pass
    return events

def emit_stream_cycle():
    events = []
    events.extend(tail_ontology(30))
    events.extend(tail_alerts(10))
    # Sort by timestamp descending
    events.sort(key=lambda e: e["ts"], reverse=True)
    # Write NDJSON
    STREAM_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STREAM_PATH, "w") as f:
        for ev in events[:50]:   # keep last 50 records
            f.write(json.dumps(ev) + "\n")
    log.info(f"Stream updated: {len(events)} events written ({STREAM_PATH})")

if __name__ == "__main__":
    while True:
        emit_stream_cycle()
        time.sleep(3)
