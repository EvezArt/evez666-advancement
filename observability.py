#!/usr/bin/env python3
"""
OBSERVABILITY LAYER - Real-time tracing + metrics
"""

import json
from datetime import datetime
from pathlib import Path
from collections import deque
import hashlib

WORKSPACE = Path("/root/.openclaw/workspace")
TRACE_DIR = WORKSPACE / "traces"
TRACE_DIR.mkdir(exist_ok=True)

# === TRACE ===
class Tracer:
    def __init__(self):
        self.traces = deque(maxlen=1000)
        self.metrics = {
            "total_requests": 0,
            "total_cost": 0.0,
            "total_revenue": 0.0,
            "conversions": 0
        }
    
    def trace(self, tenant_id, service, action, latency_ms, cost=0, outcome="success"):
        trace = {
            "trace_id": hashlib.md5(f"{datetime.now().isoformat()}{action}".encode()).hexdigest()[:12],
            "tenant_id": tenant_id,
            "timestamp": datetime.now().isoformat(),
            "service": service,
            "action": action,
            "latency_ms": latency_ms,
            "cost_usd": cost,
            "outcome": outcome
        }
        self.traces.append(trace)
        self.metrics["total_requests"] += 1
        self.metrics["total_cost"] += cost
        return trace
    
    def trace_event(self, event_type, payload):
        trace = {
            "trace_id": hashlib.md5(f"{event_type}{datetime.now().isoformat()}".encode()).hexdigest()[:12],
            "event_type": event_type,
            "payload": payload,
            "timestamp": datetime.now().isoformat()
        }
        self.traces.append(trace)
        return trace
    
    def get_metrics(self):
        return {
            **self.metrics,
            "conversion_rate": self.metrics["conversions"] / max(1, self.metrics["total_requests"]),
            "cost_per_conversion": self.metrics["total_cost"] / max(1, self.metrics["conversions"])
        }
    
    def detect_anomaly(self):
        """Simple anomaly detection"""
        alerts = []
        
        cost_per_req = self.metrics["total_cost"] / max(1, self.metrics["total_requests"])
        if cost_per_req > 0.1:
            alerts.append("HIGH_COST_PER_REQUEST")
        
        if self.metrics["conversions"] == 0 and self.metrics["total_requests"] > 100:
            alerts.append("NO_CONVERSIONS_AFTER_100_REQUESTS")
        
        return alerts
    
    def save(self):
        (TRACE_DIR / "traces.json").write_text(json.dumps(list(self.traces), indent=2))
        (TRACE_DIR / "metrics.json").write_text(json.dumps(self.get_metrics(), indent=2))

# === RUN ===
if __name__ == "__main__":
    t = Tracer()
    
    # Simulate traces
    t.trace("acme_001", "qualifier", "score_lead", 12)
    t.trace("acme_001", "gpu_router", "select_model", 840, 0.004)
    t.trace("acme_001", "composio.gmail", "send_email", 1200, 0.001)
    t.trace("acme_001", "stripe", "create_link", 300, 0.002)
    
    t.metrics["conversions"] = 2
    
    print("=== OBSERVABILITY ===")
    print(f"Traces: {len(t.traces)}")
    print(f"Metrics: {json.dumps(t.get_metrics(), indent=2)}")
    print(f"Anomalies: {t.detect_anomaly()}")
    
    t.save()
    print("\nTraces saved to:", TRACE_DIR)