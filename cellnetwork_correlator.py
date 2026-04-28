#!/usr/bin/env python3
"""
CellNetwork Event Correlator — find cross-cell patterns across quantum, threat, UAP.
Consumes detection stream from ontology + alerts file → emits Correlation entities.
"""

import json
import time
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any, Set
from collections import defaultdict
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("cellnetwork.correlator")

ALERT_LOG = Path("/root/.openclaw/workspace/memory/cellnetwork_alerts.jsonl")
ONTOLOGY_PATH = Path("/root/.openclaw/workspace/memory/ontology/graph.jsonl")
CORRELATION_LOG = Path("/root/.openclaw/workspace/memory/cellnetwork_correlations.jsonl")

# Pattern signatures (cell-type sequences within time window)
PATTERNS = {
    "quantum_uap_sync": {
        "cells": ["quantum_radar_core", "uap_sensor_01"],
        "max_gap_sec": 30,
        "description": "Quantum radar anomaly coincides with UAP sensor trigger"
    },
    "threat_uap_coincidence": {
        "cells": ["cell_threat_scanner_global", "uap_sensor_01"],
        "max_gap_sec": 300,  # 5 minutes
        "description": "Threat intel spike concurrent with UAP detection"
    },
    "multi_cell_swarm": {
        "cells": ["quantum_radar_core", "uap_sensor_01", "cell_threat_scanner_global"],
        "max_gap_sec": 60,
        "description": "Three or more cells firing within a minute"
    },
}

@dataclass
class CorrelationCandidate:
    pattern_name: str
    detection_ids: List[str]
    cell_ids: List[str]
    timestamps: List[float]
    strength: float

def load_recent_detections(minutes: int = 60) -> List[Dict]:
    """Pull Detection entities from ontology (not raw alerts)."""
    cutoff = datetime.now(timezone.utc).timestamp() - minutes*60
    detections = []
    if not ONTOLOGY_PATH.exists():
        return detections
    with open(ONTOLOGY_PATH) as f:
        for line in f:
            obj = json.loads(line)
            if obj.get("op") != "create" or obj.get("entity",{}).get("type") != "Detection":
                continue
            props = obj["entity"]["properties"]
            ts_str = props.get("timestamp","")
            try:
                ts = datetime.fromisoformat(ts_str).timestamp()
                if ts >= cutoff:
                    detections.append({
                        "id": obj["entity"]["id"],
                        "cell_id": props.get("cell_id",""),
                        "ts": ts,
                        "severity": props.get("severity",0.0),
                        "detection_type": props.get("detection_type",""),
                    })
            except: pass
    return detections

def time_window_ok(timestamps: List[float], max_gap: float) -> bool:
    if len(timestamps) < 2:
        return False
    span = max(timestamps) - min(timestamps)
    return span <= max_gap

def correlation_strength(cells: List[str], timestamps: List[float], severities: List[float]) -> float:
    """Heuristic: more cells + tighter timing + higher severity = stronger correlation."""
    if len(cells) < 2:
        return 0.0
    unique_cells = len(set(cells))
    time_span = max(timestamps) - min(timestamps)
    time_factor = math.exp(-time_span / 60.0)   # tighter = stronger
    sev_factor = sum(severities) / len(severities)
    return min(1.0, 0.4 * unique_cells + 0.4 * time_factor + 0.2 * sev_factor)

def correlate(detections: List[Dict]) -> List[CorrelationCandidate]:
    candidates = []
    for pname, pattern in PATTERNS.items():
        target_cells = set(pattern["cells"])
        max_gap = pattern["max_gap_sec"]
        # Find detection groups where all target cells are represented
        groups = defaultdict(list)
        for d in detections:
            key = d["cell_id"]
            if key in target_cells:
                groups[key].append(d)
        # Need at least one detection per cell type
        if len(groups) < len(target_cells):
            continue
        # Collect earliest detection per cell within window
        all_cells = list(groups.keys())
        for cell_subset in [all_cells]:  # expand to combinatorial later
            sub_dets = []
            for c in cell_subset:
                best = min(groups[c], key=lambda d: d["ts"])
                sub_dets.append(best)
            if time_window_ok([d["ts"] for d in sub_dets], max_gap):
                strength = correlation_strength(
                    [d["cell_id"] for d in sub_dets],
                    [d["ts"] for d in sub_dets],
                    [d["severity"] for d in sub_dets]
                )
                if strength > 0.5:
                    candidates.append(CorrelationCandidate(
                        pattern_name=pname,
                        detection_ids=[d["id"] for d in sub_dets],
                        cell_ids=[d["cell_id"] for d in sub_dets],
                        timestamps=[d["ts"] for d in sub_dets],
                        strength=round(strength, 4),
                    ))
    return candidates

def persist_correlations(candidates: List[CorrelationCandidate]):
    CORRELATION_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(CORRELATION_LOG, "a") as f:
        for c in candidates:
            record = {
                "ts": datetime.now(timezone.utc).isoformat(),
                "domain": DOMAIN_ID,
                "correlation": {
                    "pattern": c.pattern_name,
                    "detection_ids": c.detection_ids,
                    "cell_ids": c.cell_ids,
                    "strength": c.strength,
                }
            }
            f.write(json.dumps(record) + "\n")
    log.info(f"Persisted {len(candidates)} correlation(s)")

# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    detections = load_recent_detections(minutes=90)
    log.info(f"Loaded {len(detections)} recent detections")
    candidates = correlate(detections)
    for c in candidates:
        log.info(f"CORRELATION: {c.pattern_name} strength={c.strength:.2f} cells={c.cell_ids}")
    if candidates:
        persist_correlations(candidates)
