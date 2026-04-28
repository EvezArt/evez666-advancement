#!/usr/bin/env python3
"""
KILOCLAW AUTONOMOUS REVENUE LOOP - The Spine
Run: python3 kiloclaw_loop.py
"""

import subprocess
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from collections import deque
from hashlib import md5

WORKSPACE = Path("/root/.openclaw/workspace")
STATE_DIR = WORKSPACE / "state"
STATE_DIR.mkdir(exist_ok=True)

# === CONFIG ===
SCORING_THRESHOLDS = {
    "AUTO_CLOSE": 85,
    "CLOSE": 70,
    "NURTURE": 50,
}

# === STATE ===
class State:
    def __init__(self):
        self.leads = deque(maxlen=1000)
        self.events = deque(maxlen=5000)
        self.payments = deque(maxlen=500)
        self.scores = {}
        
    def load(self):
        f = STATE_DIR / "state.json"
        if f.exists():
            data = json.loads(f.read_text())
            self.leads = deque(data.get("leads", []), maxlen=1000)
            self.events = deque(data.get("events", []), maxlen=5000)
            self.payments = deque(data.get("payments", []), maxlen=500)
            self.scores = data.get("scores", {})
    
    def save(self):
        (STATE_DIR / "state.json").write_text(json.dumps({
            "leads": list(self.leads),
            "events": list(self.events),
            "payments": list(self.payments),
            "scores": self.scores,
            "saved": datetime.now().isoformat()
        }, indent=2))

# === 1. INGESTION ===
def ingest():
    """Normalize inputs from all channels"""
    events = []
    
    # Gmail - would use composio.GMAIL_FETCH_EMAILS
    # LinkedIn - would use composio.LINKEDIN_GET_MESSAGES  
    # Telegram - would use composio.TELEGRAM_GET_UPDATES
    
    # For now: generate synthetic events for testing
    synthetic = [
        {"source": "gmail", "text": "interested in AI automation", "user": "lead1@test.com"},
        {"source": "linkedin", "text": "need help with revenue", "user": "lead2@test.com"},
        {"source": "telegram", "text": "how much for bot?", "user": "lead3@test.com"},
    ]
    
    for s in synthetic:
        events.append({
            **s,
            "timestamp": datetime.now().isoformat(),
            "thread_id": md5(s["text"].encode()).hexdigest()[:8]
        })
    
    return events

# === 2. QUALIFICATION ===
def score_lead(event):
    """Score based on intent signals"""
    text = event.get("text", "").lower()
    score = 50  # baseline
    
    # High intent keywords
    if any(w in text for w in ["buy", "price", "cost", "how much", "interested", "need"]):
        score += 25
    if any(w in text for w in ["urgent", "asap", "now", "today"]):
        score += 15
    if any(w in text for w in ["demo", "trial", "start"]):
        score += 20
    
    # Source bonus
    if event.get("source") == "telegram":
        score += 10  # higher intent
    
    return min(100, score)

def decide(score):
    """Decision tree - no gray area"""
    if score >= SCORING_THRESHOLDS["AUTO_CLOSE"]:
        return "AUTO_CLOSE"
    elif score >= SCORING_THRESHOLDS["CLOSE"]:
        return "CLOSE"
    elif score >= SCORING_THRESHOLDS["NURTURE"]:
        return "NURTURE"
    return "IGNORE"

# === 3. POLICY ENGINE ===
def violates_scope(event):
    """Check fixed pricing/scope rules"""
    text = event.get("text", "").lower()
    # Block custom scope requests
    if "custom" in text or "build" in text and "from scratch" in text:
        return True
    return False

def high_risk(event):
    """Check for risky patterns"""
    text = event.get("text", "").lower()
    if "refund" in text or "lawsuit" in text or "legal" in text:
        return True
    return False

def enforce_policy(action, event):
    """Policy enforcement"""
    if violates_scope(event):
        return "ESCALATE"
    if high_risk(event):
        return "ESCALATE"
    return "EXECUTE"

# === 4. EXECUTION ===
def send_offer(event, action):
    """Send offer via email"""
    # Would use composio.GMAIL_SEND_EMAIL
    return {
        "sent": True,
        "method": "gmail",
        "to": event.get("user"),
        "action": action,
        "timestamp": datetime.now().isoformat()
    }

def send_stripe_link(event):
    """Create Stripe payment link"""
    # Would use composio.STRIPE_CREATE_PAYMENT_LINK
    return {
        "link_created": True,
        "amount": 2900,
        "currency": "usd",
        "timestamp": datetime.now().isoformat()
    }

def execute(action, event):
    """Execute the decided action"""
    if action == "AUTO_CLOSE":
        result = send_offer(event, action)
        stripe = send_stripe_link(event)
        return {"offer": result, "stripe": stripe}
    elif action == "CLOSE":
        return send_offer(event, action)
    elif action == "NURTURE":
        return {"status": "nurture", "message": "helpful reply sent"}
    return {"status": "ignored"}

def notify_slack(event):
    """Escalation notification"""
    # Would use composio.SLACK_SEND_MESSAGE
    return {"alert": True, "event": event, "timestamp": datetime.now().isoformat()}

# === 5. PAYMENT TRIGGER ===
def process_payments():
    """Check for new payments"""
    # Would use composio.STRIPE_LIST_CHARGES
    return []

def kickoff_fulfillment(payment):
    """Create Linear tasks on payment"""
    # Would use composio.LINEAR_CREATE_LINEAR_ISSUE
    return {"task_created": True, "payment": payment}

# === 6. MEMORY/LEARNING ===
def learn():
    """Update scoring weights based on outcomes"""
    # Would analyze conversion rates
    return {"model_updated": True, "timestamp": datetime.now().isoformat()}

# === MAIN LOOP ===
def run_cycle():
    state = State()
    state.load()
    
    results = {
        "ingested": 0,
        "scored": 0,
        "executed": 0,
        "escalated": 0,
        "payments": 0,
        "timestamp": datetime.now().isoformat()
    }
    
    # 1. INGEST
    events = ingest()
    results["ingested"] = len(events)
    
    for e in events:
        # 2. SCORE
        score = score_lead(e)
        e["score"] = score
        e["decision"] = decide(score)
        results["scored"] += 1
        
        # 3. POLICY
        policy = enforce_policy(e["decision"], e)
        e["policy"] = policy
        
        # 4. EXECUTE
        if policy == "EXECUTE":
            exec_result = execute(e["decision"], e)
            e["result"] = exec_result
            results["executed"] += 1
        elif policy == "ESCALATE":
            notify_slack(e)
            results["escalated"] += 1
        
        state.events.append(e)
    
    # 5. PAYMENTS
    payments = process_payments()
    results["payments"] = len(payments)
    for p in payments:
        kickoff_fulfillment(p)
        state.payments.append(p)
    
    # 6. LEARN
    learn()
    
    # Save state
    state.save()
    
    return results

# === RUN ===
if __name__ == "__main__":
    print("=== KILOCLAW AUTONOMOUS LOOP ===")
    results = run_cycle()
    print(f"Ingested: {results['ingested']}")
    print(f"Scored: {results['scored']}")
    print(f"Executed: {results['executed']}")
    print(f"Escalated: {results['escalated']}")
    print(f"Payments: {results['payments']}")
    print(json.dumps(results, indent=2, default=str))
# === BRIDGE EXECUTION (added 2026-04-22) ===
# Cognition → Action Bridge
try:
    result = subprocess.run(
        ["/usr/bin/python3", str(WORKSPACE / "evez-agentnet/cognition/action_bridge.py")],
        capture_output=True, timeout=30
    )
    if result.returncode == 0:
        print("  ✓ Cognition-Action bridge: OK")
except Exception as e:
    print(f"  ✗ Cognition-Action bridge: {e}")

# Pattern → Revenue Bridge  
try:
    result = subprocess.run(
        ["/usr/bin/python3", str(WORKSPACE / "evez-agentnet/cognition/pattern_revenue.py")],
        capture_output=True, timeout=30
    )
    if result.returncode == 0:
        print("  ✓ Pattern-Revenue bridge: OK")
except Exception as e:
    print(f"  ✗ Pattern-Revenue bridge: {e}")
