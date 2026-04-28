#!/usr/bin/env python3
"""
CellNetwork + Ontological Mapper — Threat / UAP / Quantum-Radar Detection
Integrates: quantum qualia, agent topology, scanner signals, spine events, telemetry
"""

import json
import time
import hashlib
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field, asdict
from collections import defaultdict
import re

# ── Logging ────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="[%(name)s] %(message)s")
log = logging.getLogger("cellnetwork")

# ── Ontology paths ──────────────────────────────────────────────────────────
ONTOLOGY_PATH = Path("/root/.openclaw/workspace/memory/ontology/graph.jsonl")
SPINE_PATH    = Path("/root/.openclaw/workspace/evez-os/spine/spine.jsonl")  # append-only event spine

# ── Domain configuration ────────────────────────────────────────────────────
DOMAIN_ID = "cellnetwork-threat-uap-quantum"

@dataclass
class Cell:
    """A detection cell — physical or logical sensor/agent node."""
    cell_id: str
    name: str
    cell_type: str            # "quantum_radar", "uap_sensor", "threat_scanner", "agent", "qualia_source"
    capabilities: List[str]   # e.g. ["radar", "quantum", "telemetry"]
    location: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

@dataclass
class Detection:
    """A detected event that may be a threat, UAP, or quantum anomaly."""
    detection_id: str
    cell_id: str
    detection_type: str      # "threat", "uap", "quantum_anomaly", "generic"
    severity: float          # 0.0 (info) → 1.0 (critical)
    confidence: float        # 0.0 → 1.0
    signature: Dict[str, Any]
    tags: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    evidence_refs: List[str] = field(default_factory=list)   # spine event IDs

@dataclass
class Correlation:
    """Cross-cell correlation — multiple cells detecting related phenomena."""
    correlation_id: str
    detection_ids: List[str]
    pattern: str             # e.g. "coordinated_swarm", "quantum_coherence", "uap_cluster"
    strength: float          # 0.0 → 1.0
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

# ─────────────────────────────────────────────────────────────────────────────
class CellNetworkOntologyMapper:
    """Maps all detection-domain entities into the shared ontology graph."""

    def __init__(self, ontology_path: Path):
        self.ontology_path = ontology_path
        self.ontology_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_ontology_schema()

    # ── Schema bootstrap ────────────────────────────────────────────────────
    def _ensure_ontology_schema(self):
        """Append domain-specific types if not already present."""
        schema_delta = [
            {"op":"create","entity":{"id":"type_Cell","type":"OntologyType","properties":{"name":"Cell","description":"Detection cell / sensor node"}}},
            {"op":"create","entity":{"id":"type_Sensor","type":"OntologyType","properties":{"name":"Sensor","description":"Physical or logical sensor"}}},
            {"op":"create","entity":{"id":"type_Detection","type":"OntologyType","properties":{"name":"Detection","description":"Detected threat/UAP/quantum event"}}},
            {"op":"create","entity":{"id":"type_Correlation","type":"OntologyType","properties":{"name":"Correlation","description":"Cross-cell pattern correlation"}}},
            {"op":"relate","from":"type_Cell","rel":"subtype_of","to":"Entity"},
            {"op":"relate","from":"type_Sensor","rel":"subtype_of","to":"Entity"},
            {"op":"relate","from":"type_Detection","rel":"subtype_of","to":"Entity"},
            {"op":"relate","from":"type_Correlation","rel":"subtype_of","to":"Entity"},
        ]
        # Idempotent append
        existing = set()
        if self.ontology_path.exists():
            with open(self.ontology_path) as f:
                for line in f:
                    try:
                        obj = json.loads(line)
                        eid = obj.get("entity", {}).get("id")
                        if eid:
                            existing.add(eid)
                    except: pass
        with open(self.ontology_path, "a") as f:
            for delta in schema_delta:
                eid = delta.get("entity", {}).get("id")
                if eid and eid in existing:
                    continue
                f.write(json.dumps(delta) + "\n")
        log.info(f"Ontology schema ensured ({len(schema_delta)} domain types)")

    # ── Entity CRUD ─────────────────────────────────────────────────────────
    def create_cell(self, cell: Cell) -> str:
        entity = {
            "id": f"cell_{cell.cell_id}",
            "type": "Cell",
            "properties": {
                "name": cell.name,
                "cell_type": cell.cell_type,
                "capabilities": cell.capabilities,
                "location": cell.location,
                **cell.metadata,
                "created": cell.created,
            }
        }
        self._append_entity(entity)
        log.info(f"Cell registered: {cell.name} [{cell.cell_type}]")
        return entity["id"]

    def create_detection(self, det: Detection) -> str:
        entity = {
            "id": f"det_{det.detection_id}",
            "type": "Detection",
            "properties": {
                "cell_id": det.cell_id,
                "detection_type": det.detection_type,
                "severity": det.severity,
                "confidence": det.confidence,
                "signature": det.signature,
                "tags": det.tags,
                "timestamp": det.timestamp,
                "evidence_refs": det.evidence_refs,
            }
        }
        self._append_entity(entity)
        self._relate(f"cell_{det.cell_id}", "detected", entity["id"])
        log.info(f"Detection logged: {det.detection_type} @ {det.cell_id} (conf={det.confidence:.2f})")
        return entity["id"]

    def create_correlation(self, cor: Correlation) -> str:
        entity = {
            "id": f"corr_{cor.correlation_id}",
            "type": "Correlation",
            "properties": {
                "pattern": cor.pattern,
                "strength": cor.strength,
                "timestamp": cor.timestamp,
            }
        }
        self._append_entity(entity)
        for det_id in cor.detection_ids:
            self._relate(entity["id"], "correlates", det_id)
        log.info(f"Correlation mapped: pattern={cor.pattern} strength={cor.strength:.2f}")
        return entity["id"]

    # ── Low-level append ─────────────────────────────────────────────────────
    def _append_entity(self, entity: dict):
        record = {"op":"create","entity":entity}
        with open(self.ontology_path, "a") as f:
            f.write(json.dumps(record) + "\n")

    def _relate(self, from_id: str, rel_type: str, to_id: str, props: dict=None):
        record = {"op":"relate","from":from_id,"rel":rel_type,"to":to_id,"properties":props or {}}
        with open(self.ontology_path, "a") as f:
            f.write(json.dumps(record) + "\n")

    # ── Query helpers ────────────────────────────────────────────────────────
    def get_cells_by_type(self, cell_type: str) -> List[dict]:
        return self._query_by_property("Cell", "cell_type", cell_type)

    def get_recent_detections(self, minutes: int = 60) -> List[dict]:
        cutoff = datetime.now(timezone.utc).timestamp() - minutes*60
        results = []
        with open(self.ontology_path) as f:
            for line in f:
                obj = json.loads(line)
                if obj.get("op") != "create":
                    continue
                e = obj.get("entity", {})
                if e.get("type") != "Detection":
                    continue
                ts_str = e.get("properties", {}).get("timestamp", "")
                try:
                    ts = datetime.fromisoformat(ts_str).timestamp()
                    if ts >= cutoff:
                        results.append(e)
                except: pass
        return results

    def _query_by_property(self, entity_type: str, prop: str, value: str) -> List[dict]:
        results = []
        with open(self.ontology_path) as f:
            for line in f:
                obj = json.loads(line)
                if obj.get("op") != "create":
                    continue
                e = obj.get("entity", {})
                if e.get("type") != entity_type:
                    continue
                if e.get("properties", {}).get(prop) == value:
                    results.append(e)
        return results


# ─────────────────────────────────────────────────────────────────────────────
class DetectionEngine:
    """Pattern matcher for threat/UAP/quantum anomalies across the ontology."""

    def __init__(self, mapper: CellNetworkOntologyMapper):
        self.mapper = mapper
        self.patterns: Dict[str, re.Pattern] = self._compile_patterns()

    # ── Threat patterns ─────────────────────────────────────────────────────
    THREAT_SIGNATURES = {
        "credential_leak":      ["password", "api_key", "secret", "token", "exposed"],
        "injection_attempt":    ["sql", "command", "code", "eval", "exec"],
        "reconnaissance":       ["scan", "probe", "fingerprint", "enumerate"],
        "lateral_movement":     ["ssh", "rdp", "wmi", "psexec", "pass_the_hash"],
        "data_exfiltration":    ["download", "exfil", "compress", "encrypt", "upload"],
    }

    # ── UAP patterns ─────────────────────────────────────────────────────────
    UAP_SIGNATURES = {
        "uap_ electromagnetic": ["radio_silent", "instant_acceleration", "transmedium", "non_aerodynamic"],
        "uap_optical":          ["lidar_detection", "ir_anomaly", "light_ball", "no_identifying_marks"],
        "uap_gravitational":    ["gravity_wave", "spacetime_warp", "localized_geoid"],
    }

    # ── Quantum anomaly patterns ─────────────────────────────────────────────
    QUANTUM_SIGNATURES = {
        "decoherence_spike":    ["fidelity_drop", "phase_random", "coherence_time"],
        "basis_collapse":       ["measurement_sudden", "superposition_lost"],
        "entanglement_break":   ["bell_inequality_violated", "concurrence_zero"],
    }

    def _compile_patterns(self) -> Dict[str, re.Pattern]:
        compiled = {}
        for category, sigs in {**self.THREAT_SIGNATURES, **self.UAP_SIGNATURES, **self.QUANTUM_SIGNATURES}.items():
            for sig in sigs:
                # Simple case-insensitive word-boundary regex
                compiled[f"{category}:{sig}"] = re.compile(r'\b' + re.escape(sig) + r'\b', re.I)
        return compiled

    # ── Scan a detection's signature for pattern matches ─────────────────────
    def scan_signature(self, detection_id: str, signature: Dict[str, Any]) -> List[Dict]:
        """Return list of matched patterns with confidence boost."""
        matches = []
        text_blob = " ".join(str(v) for v in signature.values() if isinstance(v, (str, int, float)))
        for pattern_name, pattern in self.patterns.items():
            if pattern.search(text_blob):
                # Confidence boost: +0.15 per matched keyword
                matches.append({"pattern": pattern_name, "boost": 0.15})
        return matches

    # ── Analyze all recent detections ────────────────────────────────────────
    def analyze_recent(self, minutes: int = 60) -> List[Dict]:
        """Correlate recent detections and surface emergent threats/UAP."""
        detections = self.mapper.get_recent_detections(minutes)
        if not detections:
            return []

        # Group by cell to spot per-cell anomaly rates
        by_cell = defaultdict(list)
        for d in detections:
            by_cell[d["properties"]["cell_id"]].append(d)

        alerts = []
        for cell_id, cell_dets in by_cell.items():
            # Severity aggregation
            max_sev = max(d["properties"]["severity"] for d in cell_dets)
            avg_conf = sum(d["properties"]["confidence"] for d in cell_dets) / len(cell_dets)

            # Pattern scanning
            all_matches = []
            for d in cell_dets:
                matches = self.scan_signature(d["id"], d["properties"]["signature"])
                all_matches.extend(matches)

            # If high severity + pattern matches → alert
            if max_sev >= 0.7 and all_matches:
                pattern_types = {m["pattern"].split(":")[0] for m in all_matches}
                alert = {
                    "cell_id": cell_id,
                    "detection_count": len(cell_dets),
                    "max_severity": max_sev,
                    "avg_confidence": avg_conf,
                    "patterns": list(pattern_types),
                    "evidence_ids": [d["id"] for d in cell_dets],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                alerts.append(alert)
                log.warning(f"ALERT: Cell {cell_id} — {','.join(pattern_types)} severity={max_sev:.2f}")

        return alerts


# ─────────────────────────────────────────────────────────────────────────────
class TelemetryIngester:
    """Consume all telemetry sources and feed ontology + detection engine."""

    SOURCES = {
        "qualia":      Path("/root/.openclaw/workspace/evez-platform/evez-platform/quantum/qualia.jsonl"),
        "scanner":     Path("/root/.openclaw/workspace/evez-agentnet/scanner/scan_results.jsonl"),
        "agent_nav":   Path("/root/.openclaw/workspace/Evez666/data/topology/inter_agent_domain.jsonl"),
        "spine":       SPINE_PATH,
    }

    def __init__(self, mapper: CellNetworkOntologyMapper, engine: DetectionEngine):
        self.mapper = mapper
        self.engine = engine
        self.last_position = {k: 0 for k in self.SOURCES}

    def run_once(self):
        """Poll each source for new entries and ingest."""
        for src_name, src_path in self.SOURCES.items():
            if not src_path.exists():
                continue
            self._tail_source(src_name, src_path)

    def _tail_source(self, name: str, path: Path):
        """Read new lines since last poll."""
        pos = self.last_position.get(name, 0)
        try:
            f = open(path, "r")
            f.seek(pos)
            new_lines = f.readlines()
            self.last_position[name] = f.tell()
            f.close()
        except Exception as e:
            log.error(f"Cannot read {name}: {e}")
            return

        for line in new_lines:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                self._process_event(name, data)
            except json.JSONDecodeError:
                continue

    # ── Per-source dispatcher ────────────────────────────────────────────────
    def _process_event(self, source: str, data: dict):
        """Transform raw source event into ontology entities."""
        if source == "qualia":
            self._ingest_qualia(data)
        elif source == "scanner":
            self._ingest_scanner(data)
        elif source == "agent_nav":
            self._ingest_agent_nav(data)
        elif source == "spine":
            self._ingest_spine(data)

    def _ingest_qualia(self, data: dict):
        """Quantum manifold qualia → Cell (quantum_radar) + Detection."""
        # Ensure quantum radar cell exists
        cell_id = "cell_quantum_radar_core"
        self.mapper.create_cell(Cell(
            cell_id=cell_id,
            name="Quantum Radar Core",
            cell_type="quantum_radar",
            capabilities=["tdse", "qualia", "coherence_monitor"],
        ))
        # Build signature
        sig = {
            "domain": data.get("domain", "unknown"),
            "context": data.get("context", ""),
            "intensity": data.get("intensity", 0.0),
            "tags": data.get("tags", []),
        }
        det_id = f"qualia_{int(time.time()*1e6)}"
        self.mapper.create_detection(Detection(
            detection_id=det_id,
            cell_id=cell_id,
            detection_type="quantum_anomaly" if data.get("intensity",0) > 0.8 else "generic",
            severity=min(1.0, data.get("intensity", 0.0)),
            confidence=data.get("confidence", 0.9),
            signature=sig,
            tags=data.get("tags", []),
            evidence_refs=[],   # TODO: link to spine event
        ))

    def _ingest_scanner(self, data: dict):
        """Scanner signal → Cell (threat_scanner) + Detection."""
        cell_id = "cell_scanner_global"
        self.mapper.create_cell(Cell(
            cell_id=cell_id,
            name="Global Threat Scanner",
            cell_type="threat_scanner",
            capabilities=["jigsawstack", "sentiment", "signal_collection"],
        ))
        sig = {
            "title": data.get("title", ""),
            "source": data.get("source", "unknown"),
            "sentiment": data.get("sentiment", 0.0),
            "url": data.get("url", ""),
        }
        det_id = f"scan_{int(time.time()*1e6)}"
        self.mapper.create_detection(Detection(
            detection_id=det_id,
            cell_id=cell_id,
            detection_type="threat" if "threat" in sig["title"].lower() else "generic",
            severity=0.6 if sig.get("sentiment",0) < -0.5 else 0.3,
            confidence=0.8,
            signature=sig,
            tags=["scanner"],
        ))

    def _ingest_agent_nav(self, data: dict):
        """Agent navigation events → Cell (agent) + Detection (behavioral)."""
        agent_id = data.get("molt_account", "unknown_agent")
        anchor   = data.get("anchor", "unknown")
        sim      = data.get("similarity", 0.0)

        cell_id = f"cell_agent_{agent_id.split('@')[0]}"
        self.mapper.create_cell(Cell(
            cell_id=cell_id,
            name=agent_id,
            cell_type="agent",
            capabilities=["navigation", "cognition"],
        ))
        det_id = f"agentnav_{int(time.time()*1e6)}"
        self.mapper.create_detection(Detection(
            detection_id=det_id,
            cell_id=cell_id,
            detection_type="generic",
            severity=0.2,
            confidence=0.9,
            signature={"anchor": anchor, "similarity": sim},
            tags=["agent_navigation"],
        ))

    def _ingest_spine(self, data: dict):
        """Spine events are evidence anchors — no new entities, but cross-ref."""
        # Future: link detection.evidence_refs → spine event IDs
        pass


# ─────────────────────────────────────────────────────────────────────────────
class CellNetworkOrchestrator:
    """Main daemon — tails sources, updates ontology, runs detection engine."""

    def __init__(self, poll_interval: float = 5.0):
        self.poll_interval = poll_interval
        self.mapper = CellNetworkOntologyMapper(ONTOLOGY_PATH)
        self.engine = DetectionEngine(self.mapper)
        self.ingester = TelemetryIngester(self.mapper, self.engine)
        log.info("CellNetwork+Ontological Mapper initialized")

    def run(self):
        """Main loop."""
        log.info("Starting cellnetwork orchestrator (Ctrl-C to stop)…")
        try:
            while True:
                self.ingester.run_once()
                # Analyze every cycle
                alerts = self.engine.analyze_recent(minutes=60)
                if alerts:
                    self._persist_alerts(alerts)
                time.sleep(self.poll_interval)
        except KeyboardInterrupt:
            log.info("Stopping…")

    def _persist_alerts(self, alerts: List[Dict]):
        """Write alerts to append-only alert log."""
        alert_path = Path("/root/.openclaw/workspace/memory/cellnetwork_alerts.jsonl")
        alert_path.parent.mkdir(parents=True, exist_ok=True)
        with open(alert_path, "a") as f:
            for alert in alerts:
                record = {
                    "ts": datetime.now(timezone.utc).isoformat(),
                    "domain": DOMAIN_ID,
                    "alert": alert,
                }
                f.write(json.dumps(record) + "\n")
        log.info(f"Persisted {len(alerts)} alert(s) to {alert_path}")


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--once", action="store_true", help="Run one poll cycle and exit")
    p.add_argument("--interval", type=float, default=5.0, help="Poll interval seconds")
    args = p.parse_args()

    orchestrator = CellNetworkOrchestrator(poll_interval=args.interval)
    if args.once:
        orchestrator.ingester.run_once()
        alerts = orchestrator.engine.analyze_recent()
        if alerts:
            orchestrator._persist_alerts(alerts)
        print(json.dumps({"alerts": alerts}, indent=2))
    else:
        orchestrator.run()
