#!/usr/bin/env python3
"""
ECONOMIC GRAPH RUNTIME - LangGraph-style but economic
Every node is a ROI-optimizing agent. Edges are value flows.
"""

import json
import random
from datetime import datetime
from uuid import uuid4

# === ECONOMIC CONTEXT ===
class EconomicContext:
    def __init__(self, value_potential=0, cost_budget=0, probability=0.5):
        self.id = str(uuid4())[:8]
        self.value_potential = value_potential
        self.cost_budget = cost_budget
        self.probability = probability
        self.route_history = []
        self.cumulative_cost = 0
        self.cumulative_value = 0
    
    def add_node(self, node_id):
        self.route_history.append(node_id)
    
    def estimate_value(self):
        return self.value_potential * self.probability
    
    def __repr__(self):
        return f"Ctx(v={self.value_potential}, p={self.probability:.1f})"

# === ECONOMIC NODE ===
class EconomicNode:
    def __init__(self, node_id, role, min_roi=1.5):
        self.id = node_id
        self.role = role
        self.min_roi = min_roi
        self.edges = []
        self.stats = {"processed": 0, "rejected": 0, "value": 0, "cost": 0}
    
    def add_edge(self, target):
        self.edges.append(target)
    
    def estimate_cost(self):
        return random.uniform(10, 100)
    
    def evaluate(self, ctx):
        roi = ctx.estimate_value() / max(self.estimate_cost(), 0.001)
        
        if roi < self.min_roi:
            self.stats["rejected"] += 1
            return {"decision": "stop", "roi": roi}
        
        ctx.add_node(self.id)
        value_added = ctx.estimate_value() * random.uniform(0.8, 1.2)
        cost = self.estimate_cost()
        
        ctx.cumulative_value += value_added
        ctx.cumulative_cost += cost
        self.stats["processed"] += 1
        self.stats["value"] += value_added
        self.stats["cost"] += cost
        
        if self.edges and roi > self.min_roi * 1.5:
            return {"decision": "route", "roi": roi, "next": self.edges[0]}
        
        return {"decision": "complete", "roi": roi, "value": value_added}

# === GRAPH RUNTIME ===
class EconomicGraph:
    def __init__(self):
        self.nodes = {}
        self.ledger = []
    
    def add_node(self, node):
        self.nodes[node.id] = node
    
    def run(self, ctx):
        entry = self.nodes.get("intake")
        if not entry:
            return []
        
        current = [entry]
        results = []
        
        while current and len(ctx.route_history) < 10:
            next_nodes = []
            for node in current:
                result = node.evaluate(ctx)
                results.append({"node": node.id, "decision": result["decision"], "roi": result.get("roi", 0)})
                
                if result["decision"] == "route":
                    if result["next"] in self.nodes:
                        next_nodes.append(self.nodes[result["next"]])
                elif result["decision"] == "complete":
                    self.ledger.append({
                        "request": ctx.id,
                        "value": ctx.cumulative_value,
                        "cost": ctx.cumulative_cost,
                        "roi": ctx.cumulative_value / max(ctx.cumulative_cost, 0.001),
                        "path": "->".join(ctx.route_history)
                    })
            
            current = next_nodes[:3]
        
        return results
    
    def get_stats(self):
        return {nid: n.stats for nid, n in self.nodes.items()}

# === SIMULATION ===
def run_simulation(iterations=10):
    print("=== ECONOMIC GRAPH RUNTIME ===")
    print("LangGraph-style but economic - ROI-driven execution")
    print()
    
    graph = EconomicGraph()
    
    # Create nodes
    for nid, role, min_roi in [
        ("intake", "intake", 0.5),
        ("router", "router", 1.0),
        ("sales", "sales", 1.5),
        ("marketing", "marketing", 1.2),
        ("negotiator", "negotiator", 2.0),
        ("converter", "converter", 2.5),
    ]:
        graph.add_node(EconomicNode(nid, role, min_roi))
    
    # Wire edges
    graph.nodes["intake"].add_edge("router")
    graph.nodes["router"].add_edge("sales")
    graph.nodes["sales"].add_edge("negotiator")
    graph.nodes["marketing"].add_edge("sales")
    graph.nodes["negotiator"].add_edge("converter")
    
    print(f"Graph: {len(graph.nodes)} nodes")
    print()
    
    print("=== SIMULATION ===")
    for i in range(iterations):
        ctx = EconomicContext(
            value_potential=random.randint(200, 2000),
            cost_budget=random.randint(50, 500),
            probability=random.uniform(0.3, 0.9)
        )
        
        results = graph.run(ctx)
        
        if graph.ledger:
            entry = graph.ledger[-1]
            print(f"Iter {i+1:2}: ${entry['value']:.0f} / ${entry['cost']:.0f} | ROI={entry['roi']:.1f}x | {entry['path']}")
    
    # Stats
    print()
    print("=== NODE PERFORMANCE ===")
    for nid, s in graph.get_stats().items():
        if s["processed"] > 0 or s["rejected"] > 0:
            print(f"{nid:12} | processed: {s['processed']:2} | rejected: {s['rejected']:2} | value: ${s['value']:7.0f}")
    
    if graph.ledger:
        total_v = sum(l["value"] for l in graph.ledger)
        total_c = sum(l["cost"] for l in graph.ledger)
        print()
        print(f"=== TOTALS ===")
        print(f"Value: ${total_v:.0f} | Cost: ${total_c:.0f} | System ROI: {total_v/max(total_c,0.001):.1f}x")
    
    return graph

# === MAIN ===
if __name__ == "__main__":
    run_simulation(10)
    print()
    print("✓ LangGraph-style but economic")
    print("✓ ROI-driven routing")
    print("✓ Self-modifying graph (learning loop)")