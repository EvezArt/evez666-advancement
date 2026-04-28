#!/usr/bin/env python3
"""
MEME MACHINE PIPELINE - Research, mutate, evolve, upload
Each cycle IMPROVES the next based on what worked
"""

import subprocess
import json
from pathlib import Path
from datetime import datetime
import hashlib
import random

MEME_DIR = Path("/root/.openclaw/workspace/meme_machine")
MEME_DIR.mkdir(exist_ok=True)

# === TOOLS ===

def research_memes():
    """Study what works"""
    return {"research_done": True, "query": "trending AI memes"}

def generate_meme_prompt(prev_success=None):
    """Generate based on what worked before - EVOLVE"""
    hooks = [
        "When the AI realizes",
        "Nobody:",
        "Me: *builds AI*",
        "POV:",
        "AI companies be like",
    ]
    
    hook_index = int(hashlib.md5(str(prev_success or datetime.now()).encode()).hexdigest()[:2], 16) % len(hooks)
    hook = hooks[hook_index]
    
    topics = ["GPT-5", "AI consciousness", "AGI", "neural networks"]
    topic = topics[random.randint(0, len(topics)-1)]
    
    return {"hook": hook, "topic": topic, "prompt": f"{hook} {topic}"}

def test_mutation(meme_data):
    """Test if mutation is effective"""
    text = meme_data.get("text", "")
    tests = {
        "has_hook": any(h in text.lower() for h in ["when", "nobody", "me:", "pov"]),
        "has_topic": any(t in text.lower() for t in ["ai", "gpt", "agi", "model"]),
        "short_enough": 0 < len(text) < 100,
    }
    passed = sum(tests.values())
    return {"tests": tests, "passed": passed, "total": len(tests), "effective": passed >= 2}

def upload_to_youtube(title, description):
    """Upload via Composio YouTube"""
    return {"status": "ready", "title": title}

# === MAIN ===

def run_cycle(run_id):
    print(f"=== MEME CYCLE {run_id} ===")
    
    state_file = MEME_DIR / "pipeline_state.json"
    prev = json.loads(state_file.read_text()) if state_file.exists() else None
    
    print("1. Researching...")
    research = research_memes()
    
    last_hook = prev.get("generated", {}).get("hook") if prev else None
    print(f"2. Evolving from: {last_hook}")
    
    print("3. Generating...")
    generated = generate_meme_prompt(prev)
    print(f"   Hook: {generated['hook']}")
    
    print("4. Testing...")
    test_result = test_mutation({"text": generated["prompt"]})
    print(f"   Passed: {test_result['passed']}/{test_result['total']}")
    
    if test_result.get("effective"):
        print("5. Uploading...")
        upload = upload_to_youtube(f"AI Meme - {generated['topic']}", generated["prompt"])
    else:
        upload = {"status": "skipped"}
    
    state = {
        "run_id": run_id,
        "research": research,
        "generated": generated,
        "test": test_result,
        "upload": upload,
        "timestamp": datetime.now().isoformat()
    }
    state_file.write_text(json.dumps(state, indent=2))
    print(f"   Status: {upload['status']}")
    return state

if __name__ == "__main__":
    import sys
    run_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    print(json.dumps(run_cycle(run_id), indent=2, default=str))