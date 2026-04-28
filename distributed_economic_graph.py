#!/usr/bin/env python3
"""
KILOCLAW DISTRIBUTED SYSTEM - Kafka + K8s Economic Graph
Production microservice architecture
"""

import json
import asyncio
import random
from datetime import datetime
from uuid import uuid4
from collections import defaultdict
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
import hashlib

# === CORE SCHEMAS ===
@dataclass
class EconomicEvent:
    trace_id: str
    node: str
    value_potential: float
    cost_budget: float
    probability: float
    timestamp: str
    route_history: List[str]
    
    @classmethod
    def create(cls, value=0, cost=0, prob=0.5):
        return cls(
            trace_id=str(uuid4())[:8],
            node="intake",
            value_potential=value,
            cost_budget=cost,
            probability=prob,
            timestamp=datetime.now().isoformat(),
            route_history=["intake"]
        )
    
    def to_kafka(self) -> dict:
        return {
            "trace_id": self.trace_id,
            "node": self.node,
            "payload": {
                "value_potential": self.value_potential,
                "cost_budget": self.cost_budget,
                "probability": self.probability
            },
            "context": {
                "graph_partition": "us-east-1",
                "priority": 0.8
            },
            "timestamp": self.timestamp
        }

@dataclass
class LedgerEntry:
    trace_id: str
    node: str
    value: float
    cost: float
    roi: float
    timestamp: str
    attribution: Dict[str, float]

# === KAFKA SIMULATION ===
class KafkaEventBus:
    """Simulated Kafka event bus"""
    def __init__(self):
        self.topics = defaultdict(list)
        self.offsets = defaultdict(int)
    
    def produce(self, topic: str, event: dict):
        self.topics[topic].append(event)
    
    def consume(self, topic: str, group_id: str) -> List[dict]:
        events = self.topics[topic][self.offsets[group_id]:]
        self.offsets[group_id] = len(self.topics[topic])
        return events
    
    def get_lag(self, topic: str) -> int:
        return len(self.topics[topic]) - self.offsets.get("consumer", 0)

# === K8S SERVICE SIMULATION ===
@dataclass
class K8sService:
    name: str
    replicas: int
    role: str
    min_roi: float
    stats: Dict
    
    def __init__(self, name, role, min_roi=1.5):
        self.name = name
        self.role = role
        self.min_roi = min_roi
        self.replicas = 1
        self.stats = {"processed": 0, "rejected": 0, "value": 0, "cost": 0}

# === AGENT MICROSERVICE ===
class AgentMicroservice:
    """Simulates a K8s agent pod"""
    def __init__(self, service: K8sService, bus: KafkaEventBus):
        self.service = service
        self.bus = bus
    
    def evaluate(self, event: EconomicEvent) -> dict:
        ctx_value = event.value_potential * event.probability
        cost = random.uniform(10, 100)
        roi = ctx_value / max(cost, 0.001)
        
        # ROI decision
        if roi < self.service.min_roi:
            self.service.stats["rejected"] += 1
            return {"decision": "drop", "roi": roi}
        
        self.service.stats["processed"] += 1
        self.service.stats["value"] += ctx_value
        self.service.stats["cost"] += cost
        
        # Route decision
        next_nodes = {
            "intake": ["router"],
            "router": ["sales", "marketing"],
            "sales": ["negotiator", "ledger"],
            "marketing": ["sales", "ledger"],
            "negotiator": ["converter", "ledger"],
            "converter": ["ledger"],
        }.get(self.service.role, ["ledger"])
        
        return {
            "decision": "route" if next_nodes != ["ledger"] else "complete",
            "roi": roi,
            "next_node": next_nodes[0],
            "value": ctx_value,
            "cost": cost
        }

# === DISTRIBUTED LEDGER ===
class DistributedLedger:
    def __init__(self):
        self.entries: List[LedgerEntry] = []
        self.agent_ledger = defaultdict(lambda: {"value": 0, "cost": 0})
    
    def record(self, trace_id, node, value, cost, roi):
        entry = LedgerEntry(
            trace_id=trace_id,
            node=node,
            value=value,
            cost=cost,
            roi=roi,
            timestamp=datetime.now().isoformat(),
            attribution={node: 1.0}
        )
        self.entries.append(entry)
        self.agent_ledger[node]["value"] += value
        self.agent_ledger[node]["cost"] += cost
    
    def get_totals(self):
        total_v = sum(e.value for e in self.entries)
        total_c = sum(e.cost for e in self.entries)
        return {
            "total_value": total_v,
            "total_cost": total_c,
            "roi": total_v / max(total_c, 0.001),
            "by_agent": dict(self.agent_ledger)
        }

# === GRAPH ROUTER SERVICE ===
class GraphRouter:
    """ROI-based routing service"""
    def __init__(self, services: Dict[str, K8sService]):
        self.services = services
        self.edge_weights = {
            "intake": {"router": 1.0},
            "router": {"sales": 0.7, "marketing": 0.3},
            "sales": {"negotiator": 0.6, "ledger": 0.4},
            "marketing": {"sales": 0.5, "ledger": 0.5},
            "negotiator": {"converter": 0.8, "ledger": 0.2},
        }
    
    def route(self, event: EconomicEvent) -> str:
        """Select next node based on ROI weights"""
        candidates = self.edge_weights.get(event.node, {})
        if not candidates:
            return "ledger"
        
        # Weighted random selection
        nodes = list(candidates.keys())
        weights = list(candidates.values())
        selected = random.choices(nodes, weights=weights)[0]
        return selected

# === LEARNING SERVICE (GRAPH MUTATION) ===
class LearningService:
    def __init__(self, ledger: DistributedLedger, router: GraphRouter, services: Dict[str, K8sService]):
        self.ledger = ledger
        self.router = router
        self.services = services
        self.iteration = 0
    
    def evaluate_and_mutate(self):
        """Self-improvement loop"""
        self.iteration += 1
        totals = self.ledger.get_totals()
        
        # Adjust edge weights based on performance
        if totals["roi"] > 10:
            # Shift toward higher-value paths
            self.router.edge_weights["router"]["sales"] = min(0.9, self.router.edge_weights["router"]["sales"] + 0.1)
            self.router.edge_weights["router"]["marketing"] = max(0.1, self.router.edge_weights["router"]["marketing"] - 0.1)
        
        # Scale replicas based on load
        for name, service in self.services.items():
            if service.stats.get("processed", 0) > 50:
                service.replicas = min(10, service.replicas + 1)
        
        return {"iteration": self.iteration, "system_roi": totals["roi"]}

# === MAIN ORCHESTRATOR ===
class DistributedEconomicGraph:
    def __init__(self):
        self.kafka = KafkaEventBus()
        self.ledger = DistributedLedger()
        
        # Create K8s services (simulated pods)
        self.services = {
            name: K8sService(name, name, min_roi)
            for name, min_roi in [
                ("intake", 0.5),
                ("router", 1.0),
                ("sales", 1.5),
                ("marketing", 1.2),
                ("negotiator", 2.0),
                ("converter", 2.5),
                ("ledger", 0.1),
            ]
        }
        
        self.agents = {
            name: AgentMicroservice(svc, self.kafka)
            for name, svc in self.services.items()
        }
        
        self.router = GraphRouter(self.services)
        self.learning = LearningService(self.ledger, self.router, self.services)
    
    def submit_event(self, event: EconomicEvent):
        """Submit to graph via Kafka"""
        self.kafka.produce("graph.intake", event.to_kafka())
    
    def process_batch(self, limit=10):
        """Process through distributed graph"""
        results = []
        
        for i in range(limit):
            # Consume from intake
            events = self.kafka.consume("graph.intake", "processor")
            if not events:
                break
            
            for event_data in events:
                # Reconstruct event
                event = EconomicEvent(
                    trace_id=event_data["trace_id"],
                    node=event_data["node"],
                    value_potential=event_data["payload"]["value_potential"],
                    cost_budget=event_data["payload"]["cost_budget"],
                    probability=event_data["payload"]["probability"],
                    timestamp=event_data["timestamp"],
                    route_history=[event_data["node"]]
                )
                
                # Process through graph
                current = event.node
                max_hops = 8
                
                while current and max_hops > 0:
                    agent = self.agents.get(current)
                    if not agent:
                        break
                    
                    result = agent.evaluate(event)
                    event.route_history.append(current)
                    
                    if result["decision"] == "complete":
                        self.ledger.record(event.trace_id, current, result["value"], result["cost"], result["roi"])
                        results.append({"trace": event.trace_id, "roi": result["roi"], "path": "->".join(event.route_history)})
                        break
                    elif result["decision"] == "drop":
                        break
                    else:
                        # Route to next
                        next_node = self.router.route(event)
                        event.node = next_node
                        current = next_node
                        max_hops -= 1
        
        return results
    
    def run_simulation(self, iterations=10):
        print("=== DISTRIBUTED ECONOMIC GRAPH ===")
        print("Kafka + K8s Architecture")
        print()
        
        # Submit initial events
        for i in range(iterations):
            event = EconomicEvent.create(
                value=random.randint(200, 2000),
                cost=random.randint(50, 500),
                prob=random.uniform(0.3, 0.9)
            )
            self.submit_event(event)
        
        print(f"Submitted {iterations} events to Kafka")
        print()
        
        # Process through graph
        results = self.process_batch(iterations)
        
        for r in results:
            print(f"  {r['trace']}: ROI={r['roi']:.1f}x | {r['path']}")
        
        # Get totals
        totals = self.ledger.get_totals()
        print()
        print("=== LEDGER TOTALS ===")
        print(f"Value: ${totals['total_value']:.0f}")
        print(f"Cost: ${totals['total_cost']:.0f}")
        print(f"System ROI: {totals['roi']:.1f}x")
        
        print()
        print("=== SERVICE STATS ===")
        for name, svc in self.services.items():
            if svc.stats["processed"] > 0:
                print(f"{name:12} | reps: {svc.replicas} | processed: {svc.stats['processed']:2} | value: ${svc.stats['value']:7.0f}")
        
        # Learning loop
        mutation = self.learning.evaluate_and_mutate()
        print()
        print("=== LEARNING ===")
        print(f"Iteration: {mutation['iteration']}, System ROI: {mutation['system_roi']:.1f}x")
        
        return totals

# === MAIN ===
if __name__ == "__main__":
    system = DistributedEconomicGraph()
    system.run_simulation(10)
    
    print()
    print("=== DISTRIBUTED ARCHITECTURE ===")
    print("✓ Kafka Event Bus (simulated)")
    print("✓ K8s Service Microservices")
    print("✓ ROI-based Graph Routing")
    print("✓ Distributed Ledger")
    print("✓ Learning + Graph Mutation")
    print("✓ Auto-scaling replicas")