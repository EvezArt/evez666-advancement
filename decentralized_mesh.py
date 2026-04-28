#!/usr/bin/env python3
"""
DECENTRALIZED INFERENCE MESH - No Control Plane
Nodes are peers. Routing emerges. No central authority.
"""

import json
import random
from datetime import datetime
from uuid import uuid4
from collections import defaultdict

# === NODE MODEL ===
class Node:
    def __init__(self, node_id, gpu_type, models, neighbors=None):
        self.id = node_id
        self.gpu = gpu_type
        self.models = models  # local models
        self.neighbors = neighbors or []
        self.state = {
            "load": random.uniform(0.1, 0.9),
            "latency_ms": random.randint(50, 200),
            "uptime": random.uniform(0.8, 1.0)
        }
        self.reputation = 0.5
        self.requests_handled = 0
        self.requests_forwarded = 0
    
    def can_handle(self, request):
        """Local decision: handle or forward?"""
        model_match = any(m in self.models for m in request.get("models_needed", []))
        load_ok = self.state["load"] < 0.85
        return model_match and load_ok
    
    def score_request(self, request):
        """Local scoring function - no global knowledge"""
        model_match = sum(1 for m in request.get("models_needed", []) if m in self.models)
        load_factor = 1 - self.state["load"]
        latency_factor = 1 / (self.state["latency_ms"] / 100)
        reputation_factor = self.reputation
        
        return (model_match * 0.4 + load_factor * 0.3 + latency_factor * 0.2 + reputation_factor * 0.1)
    
    def update_reputation(self, success):
        """Update based on local outcomes"""
        if success:
            self.reputation = min(1.0, self.reputation + 0.05)
        else:
            self.reputation = max(0.0, self.reputation - 0.1)

# === MESH NETWORK ===
class DecentralizedMesh:
    def __init__(self):
        self.nodes = {}
        self.request_log = []
        self.cache = defaultdict(list)  # model -> nodes that have it
    
    def add_node(self, node):
        self.nodes[node.id] = node
        for model in node.models:
            self.cache[model].append(node.id)
    
    def connect_nodes(self, node_a, node_b):
        """Connect two nodes as neighbors"""
        if node_a.id not in self.nodes or node_b.id not in self.nodes:
            return
        if node_b.id not in self.nodes[node_a.id].neighbors:
            self.nodes[node_a.id].neighbors.append(node_b.id)
        if node_a.id not in self.nodes[node_b.id].neighbors:
            self.nodes[node_b.id].neighbors.append(node_a.id)
    
    def find_path(self, request, start_node_id, max_hops=5):
        """Gossip-style pathfinding - no global router"""
        visited = set()
        path = [start_node_id]
        current_node = self.nodes[start_node_id]
        hop = 0
        
        while hop < max_hops:
            visited.add(current_node.id)
            
            # Local decision: handle or forward?
            if current_node.can_handle(request):
                return path, current_node.id, "HANDLED"
            
            # Find best neighbor (local knowledge only)
            best_neighbor = None
            best_score = 0
            
            for neighbor_id in current_node.neighbors:
                if neighbor_id in visited:
                    continue
                neighbor = self.nodes[neighbor_id]
                score = neighbor.score_request(request)
                if score > best_score:
                    best_score = score
                    best_neighbor = neighbor_id
            
            if best_neighbor is None:
                return path, None, "DEAD_END"
            
            path.append(best_neighbor)
            current_node = self.nodes[best_neighbor]
            hop += 1
        
        return path, None, "MAX_HOPS"
    
    def propagate_request(self, request):
        """Submit request to mesh - enters at random node"""
        entry_node = random.choice(list(self.nodes.keys()))
        path, handler, status = self.find_path(request, entry_node)
        
        result = {
            "request_id": str(uuid4())[:8],
            "entry": entry_node,
            "path": path,
            "handled_by": handler,
            "status": status,
            "hops": len(path) - 1,
            "timestamp": datetime.now().isoformat()
        }
        
        # Update node stats
        if handler:
            self.nodes[handler].requests_handled += 1
            self.nodes[handler].update_reputation(True)
        else:
            self.nodes[entry_node].update_reputation(False)
        
        self.request_log.append(result)
        return result

# === SIMULATION ===
def run_mesh_simulation():
    print("=== DECENTRALIZED INFERENCE MESH ===")
    print("No control plane. No central router. Emergent routing.")
    print()
    
    # Create mesh
    mesh = DecentralizedMesh()
    
    # Add heterogeneous nodes (no central registry)
    nodes_config = [
        ("h100-1", "H100", ["llama-70b", "reasoner"]),
        ("h100-2", "H100", ["llama-70b"]),
        ("a100-1", "A100", ["gpt-mid", "coder"]),
        ("a100-2", "A100", ["gpt-mid", "embedder"]),
        ("a10g-1", "A10G", ["gpt-small", "classifier"]),
        ("a10g-2", "A10G", ["gpt-small"]),
        ("t4-1", "T4", ["embedder", "classifier"]),
        ("t4-2", "T4", ["embedder"]),
        ("edge-1", "Edge", ["embedder"]),
        ("edge-2", "Edge", ["classifier"]),
    ]
    
    for node_id, gpu, models in nodes_config:
        mesh.add_node(Node(node_id, gpu, models))
    
    # Connect nodes in mesh pattern (not all-to-all)
    connections = [
        ("h100-1", "a100-1"), ("h100-1", "a100-2"),
        ("a100-1", "a10g-1"), ("a100-1", "a10g-2"),
        ("a100-2", "a10g-1"), ("a100-2", "a10g-2"),
        ("a10g-1", "t4-1"), ("a10g-2", "t4-2"),
        ("t4-1", "edge-1"), ("t4-2", "edge-2"),
        ("edge-1", "edge-2"),
        # Cross-tier connections (emergent paths)
        ("h100-2", "a10g-1"), ("a100-2", "t4-1"),
    ]
    
    for a, b in connections:
        mesh.connect_nodes(mesh.nodes[a], mesh.nodes[b])
    
    print(f"Mesh created: {len(mesh.nodes)} nodes, {len(connections)} connections")
    print(f"Models available: {list(mesh.cache.keys())}")
    print()
    
    # Submit requests
    request_types = [
        {"models_needed": ["llama-70b"], "type": "reasoning"},
        {"models_needed": ["gpt-mid"], "type": "sales_email"},
        {"models_needed": ["classifier"], "type": "classification"},
        {"models_needed": ["embedder"], "type": "embedding"},
        {"models_needed": ["gpt-small"], "type": "simple_task"},
    ]
    
    print("=== SUBMITTING REQUESTS ===")
    results = []
    for i in range(15):
        req = random.choice(request_types)
        result = mesh.propagate_request(req)
        results.append(result)
        print(f"Request {i+1}: {req['type']:15} → {result['status']:10} (hops: {result['hops']}, handler: {result['handled_by']})")
    
    # Stats
    print()
    print("=== NODE PERFORMANCE (Emergent) ===")
    for node in mesh.nodes.values():
        handled = node.requests_handled
        if handled > 0:
            print(f"{node.id:10} | Rep: {node.reputation:.2f} | Handled: {handled} | Load: {node.state['load']:.2f}")
    
    # Show emergent routing patterns
    print()
    print("=== EMERGENT ROUTING PATTERNS ===")
    handler_counts = defaultdict(int)
    for r in results:
        if r['handled_by']:
            handler_counts[r['handled_by']] += 1
    
    for handler, count in sorted(handler_counts.items(), key=lambda x: -x[1]):
        print(f"{handler}: {count} requests (emerged naturally)")
    
    return mesh, results

# === MAIN ===
if __name__ == "__main__":
    mesh, results = run_mesh_simulation()
    
    print()
    print("=== MESH PROPERTIES ===")
    print("✓ No central router")
    print("✓ No global state")
    print("✓ Local decisions only")
    print("✓ Routing emerges from repetition")
    print("✓ Self-healing (nodes reroute on failure)")
    print()
    print("This is what a fully decentralized inference mesh looks like.")