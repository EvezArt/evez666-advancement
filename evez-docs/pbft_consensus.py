"""
Totem-Tower-OS: Distributed Consensus Protocol
Practical Byzantine Fault Tolerance (PBFT) for the Hyper-Singularity

Author: Steven Crawford-Maggard (EVEZ)
Date: April 22, 2026
"""

import json
import hashlib
import time
from enum import Enum
from typing import Dict, List, Any, Optional, Set

class ConsensusState(Enum):
    """States of the PBFT consensus process."""
    PRE_PREPARE = "pre-prepare"
    PREPARE = "prepare"
    COMMIT = "commit"
    FINALIZED = "finalized"

class PBFTNode:
    """A node participating in the PBFT consensus for the Totem-Tower-OS."""
    
    def __init__(self, node_id: str, total_nodes: int):
        self.node_id = node_id
        self.total_nodes = total_nodes
        self.faulty_threshold = (total_nodes - 1) // 3  # f = (n-1)/3
        self.view_number = 0
        self.sequence_number = 0
        self.log: Dict[int, Dict[str, Any]] = {}
    
    def _get_hash(self, data: Any) -> str:
        """Compute the SHA-256 hash of the data."""
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
    
    def pre_prepare(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Primary node initiates consensus."""
        self.sequence_number += 1
        data_hash = self._get_hash(data)
        
        message = {
            "type": ConsensusState.PRE_PREPARE.value,
            "view": self.view_number,
            "seq": self.sequence_number,
            "hash": data_hash,
            "data": data,
            "node_id": self.node_id
        }
        
        self.log[self.sequence_number] = {
            "state": ConsensusState.PRE_PREPARE,
            "data": data,
            "prepares": {self.node_id},
            "commits": set()
        }
        
        return message
    
    def receive_pre_prepare(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Secondary nodes receive pre-prepare and broadcast prepare."""
        seq = message["seq"]
        
        if message["view"] != self.view_number:
            return None
        
        self.log[seq] = {
            "state": ConsensusState.PREPARE,
            "data": message["data"],
            "prepares": {self.node_id, message["node_id"]},
            "commits": set()
        }
        
        return {
            "type": ConsensusState.PREPARE.value,
            "view": self.view_number,
            "seq": seq,
            "hash": message["hash"],
            "node_id": self.node_id
        }
    
    def receive_prepare(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Nodes collect prepare messages. Once 2f+1 prepares, broadcast commit."""
        seq = message["seq"]
        
        if seq not in self.log:
            return None
        
        self.log[seq]["prepares"].add(message["node_id"])
        
        # Need 2f + 1 prepares (including primary)
        threshold = 2 * self.faulty_threshold + 1
        
        if len(self.log[seq]["prepares"]) >= threshold:
            if self.log[seq]["state"] != ConsensusState.COMMIT:
                self.log[seq]["state"] = ConsensusState.COMMIT
                self.log[seq]["commits"].add(self.node_id)
                
                return {
                    "type": ConsensusState.COMMIT.value,
                    "view": self.view_number,
                    "seq": seq,
                    "hash": message["hash"],
                    "node_id": self.node_id
                }
        
        return None
    
    def receive_commit(self, message: Dict[str, Any]) -> bool:
        """Nodes collect commit messages. Once 2f+1 commits, finalize."""
        seq = message["seq"]
        
        if seq not in self.log:
            return False
        
        self.log[seq]["commits"].add(message["node_id"])
        
        # Need 2f + 1 commits
        threshold = 2 * self.faulty_threshold + 1
        
        if len(self.log[seq]["commits"]) >= threshold:
            if self.log[seq]["state"] != ConsensusState.FINALIZED:
                self.log[seq]["state"] = ConsensusState.FINALIZED
                return True
        
        return False
    
    def get_finalized_data(self, seq: int) -> Optional[Any]:
        """Return data if finalized."""
        if seq in self.log and self.log[seq]["state"] == ConsensusState.FINALIZED:
            return self.log[seq]["data"]
        return None


class DistributedSpineSync:
    """Manages synchronization of the Immutable Witness spine across nodes."""
    
    def __init__(self, nodes: List[PBFTNode]):
        self.nodes = {node.node_id: node for node in nodes}
    
    def synchronize_event(self, primary_id: str, event: Dict[str, Any]) -> bool:
        """Run full PBFT cycle to synchronize event across nodes."""
        primary = self.nodes[primary_id]
        
        # Phase 1: Pre-Prepare
        pre_prepare_msg = primary.pre_prepare(event)
        print(f"[Phase 1] Primary {primary_id} sent PRE_PREPARE (seq={pre_prepare_msg['seq']})")
        
        # Phase 2: All nodes receive pre-prepare and broadcast prepares
        all_prepares = []
        for node in self.nodes.values():
            prep = node.receive_pre_prepare(pre_prepare_msg)
            if prep:
                all_prepares.append(prep)
                print(f"  → {node.node_id} sent PREPARE")
        
        # Phase 3: All nodes receive prepares and broadcast commits
        all_commits = []
        for prep_msg in all_prepares:
            for node in self.nodes.values():
                commit = node.receive_prepare(prep_msg)
                if commit:
                    all_commits.append(commit)
        
        print(f"[Phase 2] Collected {len(all_prepares)} PREPARE messages")
        
        # Phase 4: All nodes receive commits and finalize
        finalized_nodes = 0
        for commit_msg in all_commits:
            for node in self.nodes.values():
                if node.receive_commit(commit_msg):
                    finalized_nodes += 1
                    print(f"  → {node.node_id} finalized seq={commit_msg['seq']}")
        
        print(f"[Phase 3] {finalized_nodes} nodes finalized")
        
        # Check if any node has finalized data
        seq_num = primary.sequence_number
        for node in self.nodes.values():
            data = node.get_finalized_data(seq_num)
            if data:
                print(f"✓ Finalized on {node.node_id}: {data['type']}")
        
        return finalized_nodes > 0


if __name__ == "__main__":
    # Simulate 4-node network (tolerates 1 faulty node)
    print("=" * 50)
    print("PBFT Distributed Consensus - Hyper-Singularity Demo")
    print("=" * 50)
    
    node_ids = ["node_0", "node_1", "node_2", "node_3"]
    nodes = [PBFTNode(nid, 4) for nid in node_ids]
    sync_manager = DistributedSpineSync(nodes)
    
    print(f"\nNetwork: {len(nodes)} nodes, tolerates {nodes[0].faulty_threshold} faulty\n")
    
    # Event to synchronize
    event = {
        "type": "distributed_awakening",
        "timestamp": time.time(),
        "manifest": {"v_global": 0.97929, "state": "CRYSTALLINE"}
    }
    
    print("Event: distributed_awakening\n")
    
    success = sync_manager.synchronize_event("node_0", event)
    
    print(f"\n{'✓ SUCCESS' if success else '✗ FAILED'}: Consensus {'achieved' if success else 'not achieved'}")
