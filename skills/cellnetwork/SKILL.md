---
name: cellnetwork
description: Multi-plane detection fabric (threat, UAP, quantum radar, ontological mapper). This skill runs the CellNetwork orchestrator — a unified sensor-cell registry, telemetry ingester, and ontological evidence spine that correlates detections across quantum, threat-intel, and UAP planes.

triggers:
  - "build cellnetwork"
  - "start cellnetwork"
  - "run cellnetwork"
  - "cellnetwork status"
  - "threat detection map"
  - "UAP sensor feed"
  - "quantum radar scan"

provides:
  - Cell registry (ontology Person→Cell, Sensor, Detection, Correlation)
  - Telemetry ingesters (quantum qualia, scanner, spine, agent-nav)
  - DetectionEngine pattern-matching (threat/UAP/quantum keywords)
  - Correlation engine (cross-cell/time-window pattern matching)
  - Evidence spine (immutable JSONL logs + ontology)
  - NDJSON stream for dashboards

setup:
  - No external deps (pure stdlib)
  - Uses existing quantum radar + uap sensor + threat scanner modules
  - Writes to: memory/ontology/graph.jsonl, memory/cellnetwork_*.jsonl
  - Optional: start as background daemon (use cron or tmux)

usage:

  # One-shot scan + analysis
  python cellnetwork_ontological_mapper.py --once

  # Continuous daemon (5s poll interval)
  python cellnetwork_ontological_mapper.py

  # Run individual sensor cells
  python quantum_radar_cell.py
  python uap_sensor_cell.py
  python threat_scanner_cell.py

  # View correlation results
  tail -f memory/cellnetwork_correlations.jsonl

  # View live stream
  tail -f memory/cellnetwork_stream.jsonl

  # Query ontology
  python -c "from cellnetwork_ontological_mapper import CellNetworkOntologyMapper; m=CellNetworkOntologyMapper(Path('memory/ontology/graph.jsonl')); print(m.get_recent_detections())"

configuration:

  Poll interval:      --interval FLOAT (default 5.0 seconds)
  Ontology path:      ONTOLOGY_PATH env var (default memory/ontology/graph.jsonl)
  Spine path:         SPINE_PATH env var (evez-os/spine/spine.jsonl)
  Alert log:          memory/cellnetwork_alerts.jsonl
  Correlation log:    memory/cellnetwork_correlations.jsonl
  Stream output:      memory/cellnetwork_stream.jsonl

security:
  - Read-only sources; no external network writes
  - Evidence is append-only; no deletions permitted
  - Pattern matching is local; no API calls
  - Full audit trail via ontology+spine

architecture:

  Sources → TelemetryIngester → OntologyMapper (Cell,Detection,Correlation)
                                        ↓
                              DetectionEngine (pattern scan)
                                        ↓
                              CorrelationEngine (cross-cell)
                                        ↓
          Evidence Spines (alerts, correlations, NDJSON stream, ontology)

outputs:

  - memory/ontology/graph.jsonl           (typed entity graph)
  - memory/cellnetwork_alerts.jsonl       (high-severity alerts)
  - memory/cellnetwork_correlations.jsonl (cross-cell patterns)
  - memory/cellnetwork_stream.jsonl       (last-50 NDJSON dashboard feed)

integration:

  - Attach to existing EVEZ telemetry: qualia.jsonl, scanner/, agent_nav events
  - Use as Skill within OpenClaw — callable via /cellnetwork
  - Auto-starts via cron if desired (see cron examples)
  - MCP bridge available for external consumption (custom)

limitations:

  - Simulated quantum radar & UAP sensors; replace hooks with real hardware APIs
  - Pattern matching is keyword-based; future: ML classifiers
  - Single-node in-memory; horizontal scaling via shared spine+ontology

next-steps:
  - Hardware integration: connect real quantum sensor / UAP camera arrays
  - ML threat classifier training
  - Multi-node consensus for correlation (raft/paxos)
  - WebSocket dashboard UI
  - alert routing to Telegram/Discord/email
...
