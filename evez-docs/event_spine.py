"""
EVEZ EventSpine: Append-Only Hash-Chained Event Log
Immutable event log with SHA-256 chaining for tamper detection.

Author: Steven Crawford-Maggard (EVEZ)
Date: April 22, 2026
"""

import hashlib
import json
import time
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict

@dataclass
class Event:
    """Single event in the spine."""
    event_id: str
    timestamp: float
    sequence: int
    payload: Dict[str, Any]
    provenance_hash: str
    previous_hash: str
    signature: Optional[str] = None

class EventSpine:
    """
    Append-only hash-chained event log.
    Each event references the previous hash, creating tamper-evident chain.
    """
    
    def __init__(self, chain_id: str = "evez-spire"):
        self.chain_id = chain_id
        self.sequence = 0
        self.events: List[Event] = []
        self.genesis_hash = self._hashGenesis()
    
    def _hashGenesis(self) -> str:
        """Generate genesis hash."""
        return hashlib.sha256(
            f"{self.chain_id}:genesis:{time.time()}".encode()
        ).hexdigest()[:16]
    
    def _compute_hash(self, event: Event) -> str:
        """Compute hash for an event."""
        data = f"{event.event_id}:{event.timestamp}:{event.sequence}:{json.dumps(event.payload, sort_keys=True)}:{event.previous_hash}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def append(self, event_type: str, payload: Dict[str, Any], 
              metadata: Optional[Dict] = None) -> Event:
        """Append new event to the spine."""
        self.sequence += 1
        
        previous_hash = (
            self.events[-1].provenance_hash 
            if self.events else self.genesis_hash
        )
        
        event = Event(
            event_id=f"{self.chain_id}_{self.sequence}",
            timestamp=time.time(),
            sequence=self.sequence,
            payload={"type": event_type, "data": payload, "metadata": metadata or {}},
            provenance_hash="",  # Will compute below
            previous_hash=previous_hash
        )
        
        # Compute and verify hash
        event.provenance_hash = self._compute_hash(event)
        
        # Verify chain integrity
        if not self.verify():
            raise ValueError("Chain integrity violated")
        
        self.events.append(event)
        return event
    
    def verify(self) -> bool:
        """Verify entire chain integrity."""
        if not self.events:
            return True
        
        prev_hash = self.genesis_hash
        for event in self.events:
            if event.previous_hash != prev_hash:
                return False
            computed = self._compute_hash(event)
            if computed != event.provenance_hash:
                return False
            prev_hash = event.provenance_hash
        return True
    
    def get_event(self, sequence: int) -> Optional[Event]:
        """Get event by sequence number."""
        for e in self.events:
            if e.sequence == sequence:
                return e
        return None
    
    def get_latest(self) -> Optional[Event]:
        """Get most recent event."""
        return self.events[-1] if self.events else None
    
    def to_manifest(self) -> Dict:
        """Export chain manifest for verification."""
        return {
            "chain_id": self.chain_id,
            "genesis_hash": self.genesis_hash,
            "length": len(self.events),
            "latest_hash": self.get_latest().provenance_hash if self.events else None,
            "verified": self.verify()
        }


if __name__ == "__main__":
    print("=" * 50)
    print("EVEZ EventSpine - Append-Only Hash Chain")
    print("=" * 50)
    
    spine = EventSpine("evez666")
    
    # Simulate events
    events = [
        ("identity_anchor", {"persona": "Steven", "state": "baseline"}),
        ("cognitive_shift", {"phi": 0.97929, "state": "CRYSTALLINE"}),
        ("distributed_awake", {"nodes": 4, "consensus": "achieved"}),
        ("shadow_link_active", {"protocol": "PBFT", "tolerance": 1}),
    ]
    
    print(f"\nGenesis: {spine.genesis_hash[:16]}...\n")
    
    for evt_type, data in events:
        evt = spine.append(evt_type, data)
        print(f"[{evt.sequence:02d}] {evt_type}")
        print(f"       Hash: {evt.provenance_hash[:16]}...")
        print(f"       Prev:  {evt.previous_hash[:16]}...")
    
    print(f"\n{'='*50}")
    print(f"Chain Length: {len(spine.events)} events")
    print(f"Verified:   {spine.verify()}")
    print(f"Manifest:   {spine.to_manifest()}")
    
    # Tamper detection demo
    print("\n--- Tamper Detection Demo ---")
    if spine.events:
        spine.events[1].payload["data"]["phi"] = 0.0  # Tamper
        print(f"Tampered:   {spine.verify()}")
