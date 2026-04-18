#!/usr/bin/env python3
"""
EVEZ CONTROL PLANE - Model Registry & Lineage
Simple but real tracking of models, data, and code versions
"""

import json
import hashlib
import os
from datetime import datetime
from pathlib import Path

REGISTRY_DIR = "/root/.openclaw/workspace/registry"
MODELS_DIR = f"{REGISTRY_DIR}/models"
LINEAGE_DIR = f"{REGISTRY_DIR}/lineage"
INDEX_FILE = f"{REGISTRY_DIR}/index.json"

class ControlPlane:
    def __init__(self):
        os.makedirs(MODELS_DIR, exist_ok=True)
        os.makedirs(LINEAGE_DIR, exist_ok=True)
        self.index = self.load_index()
    
    def load_index(self):
        if os.path.exists(INDEX_FILE):
            with open(INDEX_FILE) as f:
                return json.load(f)
        return {"models": {}, "deployments": [], "lineage": []}
    
    def save_index(self):
        with open(INDEX_FILE, 'w') as f:
            json.dump(self.index, f, indent=2)
    
    def register_model(self, name: str, version: str, data_hash: str, code_hash: str, metrics: dict = None):
        """Register a new model version with full lineage"""
        model_id = f"{name}-{version}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        record = {
            "id": model_id,
            "name": name,
            "version": version,
            "data_hash": data_hash,
            "code_hash": code_hash,
            "metrics": metrics or {},
            "registered_at": datetime.now().isoformat(),
            "status": "staging"
        }
        
        self.index["models"][model_id] = record
        self.save_index()
        
        # Create lineage entry
        self.add_lineage(model_id, "created", {
            "data": data_hash,
            "code": code_hash
        })
        
        return model_id
    
    def add_lineage(self, model_id: str, event: str, details: dict):
        """Track lineage events"""
        entry = {
            "model_id": model_id,
            "event": event,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.index["lineage"].append(entry)
        self.save_index()
    
    def promote(self, model_id: str, environment: str = "production"):
        """Promote model to environment"""
        if model_id in self.index["models"]:
            self.index["models"][model_id]["status"] = environment
            self.index["models"][model_id]["promoted_at"] = datetime.now().isoformat()
            self.add_lineage(model_id, f"promoted_to_{environment}", {})
            self.save_index()
            return True
        return False
    
    def get_model(self, model_id: str):
        return self.index["models"].get(model_id)
    
    def list_models(self, status: str = None):
        models = list(self.index["models"].values())
        if status:
            models = [m for m in models if m.get("status") == status]
        return models
    
    def get_lineage(self, model_id: str):
        return [e for e in self.index["lineage"] if e.get("model_id") == model_id]

def hash_file(path: str) -> str:
    """Generate hash of a file"""
    if not os.path.exists(path):
        return "none"
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]

if __name__ == "__main__":
    cp = ControlPlane()
    
    # Track current quantum model
    model_id = cp.register_model(
        name="evez-quantum",
        version="1.0.0",
        data_hash=hash_file("/root/.openclaw/workspace/ml/evez_omni.py"),
        code_hash=hash_file("/root/.openclaw/workspace/skills/quantum-ez/quantum_ez.py"),
        metrics={"last_accuracy": 0.95, "last_execution_ms": 1200}
    )
    
    # Get current state
    models = cp.list_models()
    print(f"REGISTERED MODELS: {len(models)}")
    for m in models:
        print(f"  - {m['id']}: {m['status']}")
    
    print(f"LINEAGE EVENTS: {len(cp.index['lineage'])}")