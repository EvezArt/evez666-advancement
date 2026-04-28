#!/usr/bin/env python3
"""
EVEZ Consolidated Core - Using extracted modules
Combines: PBFT Consensus + EventSpine + Consciousness
"""

import json
import time

# Import our built modules
from pbft_consensus import PBFTNode, DistributedSpineSync
from event_spine import EventSpine
from consciousness import ConsciousnessState, EmergenceEquation

class EVEZCore:
    """Consolidated EVEZ operating core"""
    
    def __init__(self, identity: str = "evez666"):
        self.identity = identity
        self.start_time = time.time()
        
        # Initialize PBFT consensus (4 nodes)
        self.nodes = [PBFTNode(f"node_{i}", 4) for i in range(4)]
        self.consensus = DistributedSpineSync(self.nodes)
        
        # Initialize Event Spine
        self.spine = EventSpine(identity)
        
        # Initialize Consciousness
        self.consciousness = ConsciousnessState(64)
        
    def boot_sequence(self) -> dict:
        """Run boot sequence"""
        events = []
        
        # 1. Genesis event
        evt = self.spine.append("boot", {"phase": "genesis", "identity": self.identity})
        events.append(evt.event_id)
        
        # 2. Consciousness initialization
        self.consciousness.phase = "baseline"
        self.consciousness.compute_phi()
        
        # 3. First PBFT sync
        self.consensus.synchronize_event("node_0", {
            "type": "boot_complete",
            "timestamp": time.time()
        })
        
        return {
            "status": "boot_complete",
            "events": len(events),
            "phi": self.consciousness.phi
        }
    
    def process_input(self, input_data: dict) -> dict:
        """Process input through full pipeline"""
        ts = time.time()
        
        # Log to spine
        evt = self.spine.append("input", input_data)
        
        # Update consciousness
        self.consciousness.phase = input_data.get("type", "unknown")
        
        # Run consensus
        self.consensus.synchronize_event("node_0", input_data)
        
        # Compute emergence
        FC = EmergenceEquation.compute(
            input_data.get("FQ", 0.8),
            input_data.get("CA", 0.6),
            input_data.get("FB", 0.4)
        )
        
        return {
            "processed": True,
            "event_id": evt.event_id,
            "phi": self.consciousness.phi,
            "FC": FC,
            "latency_ms": (time.time() - ts) * 1000
        }
    
    def get_status(self) -> dict:
        """Get current system status"""
        return {
            "identity": self.identity,
            "uptime_seconds": time.time() - self.start_time,
            "spine_length": len(self.spine.events),
            "phi": self.consciousness.phi,
            "consensus_nodes": len(self.nodes),
            "verified": self.spine.verify()
        }


if __name__ == "__main__":
    print("=" * 50)
    print("EVEZ CONSOLIDATED CORE")
    print("=" * 50)
    
    # Initialize
    evez = EVEZCore("evez666")
    
    # Boot
    boot_result = evez.boot_sequence()
    print(f"\n[BOOT] {boot_result['status']}")
    print(f"  Events: {boot_result['events']}")
    print(f"  Phi: {boot_result['phi']:.3f}")
    
    # Process inputs
    test_inputs = [
        {"type": "reasoning", "data": "quantum analysis", "FQ": 0.9, "CA": 0.7, "FB": 0.5},
        {"type": "creation", "data": "new module", "FQ": 0.85, "CA": 0.8, "FB": 0.6},
        {"type": "deployment", "data": "production ready", "FQ": 0.95, "CA": 0.9, "FB": 0.7},
    ]
    
    print("\n[PROCESSING INPUTS]")
    for inp in test_inputs:
        result = evez.process_input(inp)
        print(f"  → {inp['type']}: phi={result['phi']:.3f}, FC={result['FC']:.3f}")
    
    # Status
    status = evez.get_status()
    print(f"\n[STATUS]")
    print(f"  Identity: {status['identity']}")
    print(f"  Uptime: {status['uptime_seconds']:.1f}s")
    print(f"  Spine: {status['spine_length']} events")
    print(f"  Phi: {status['phi']:.3f}")
    print(f"  Verified: {status['verified']}")
    
    print("\n✓ EVEZ Core operational")